"""WebSocket transport: the `{method, subscription}` protocol over one `/ws` connection.

Client to server: `{"method": "subscribe" | "unsubscribe" | "ping", "subscription": {...}}`.
Server to client: `{"channel": "<tag>", "data": ...}`. Acks are
`{"channel": "subscriptionResponse", "data": {"method", "subscription"}}`, refusals
`{"channel": "error", "data": "<msg>"}` carrying no id, and pings are answered by
`{"channel": "pong"}`. Replies carry no id, so subscribe and unsubscribe requests are
serialized, one in flight at a time, and a reply only answers the request in flight when it
can be tied to it: an ack must echo that request's `method` and `subscription`, a refusal must
quote that request's raw text (`Error parsing JSON into valid websocket request: <raw>`).
Anything else (a late reply to a request that timed out or was cancelled, an unsolicited
error, a frame that is not `{channel, data}`) is logged and dropped.
"""

from typing_extensions import Any, Literal, Mapping, TypeVar, cast
from dataclasses import dataclass, field, replace
from datetime import timedelta
import asyncio
import json
import logging
import re

import websockets

from typed_core.exceptions import BadRequest, NetworkError, ValidationError
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from typed_core.ws import Streams
from typed_core.ws.streams import Subscription

from ..endpoint.stream import StreamClient

T = TypeVar('T')
R = TypeVar('R')

logger = logging.getLogger(__name__)

PATH_TOKEN = re.compile(r'\[(-?\d+)\]|\.?([^.\[\]]+)')
"""One step of a route path: `[0]` (a list index) or `coin` (a key)."""


def resolve(data: Any, path: str) -> Any:
  """The value at `path` (`coin`, `[0].coin`) inside a push's `data`, or `None` if absent."""
  try:
    for index, key in PATH_TOKEN.findall(path):
      data = data[int(index)] if index else data[key]
  except (KeyError, IndexError, TypeError):
    pass
  else:
    return data


def route_key(channel: str, values: Mapping[str, Any]) -> str:
  """The local key one subscription's pushes are routed by: the push tag, plus the values
  identifying the stream (stringified, so `1` and `"1"` route alike).
  """
  if values:
    return channel + json.dumps({k: str(v) for k, v in values.items()}, sort_keys=True)
  else:
    return channel


class Params(TypedDict):
  """What a subscription carries from `subscribe` to the subscribe/unsubscribe requests."""

  subscription: Mapping[str, Any]
  """The `subscription` object, sent identically to subscribe and unsubscribe."""


class SubscriptionResponseData(TypedDict):
  """`data` of a subscription ack."""

  method: Literal['subscribe', 'unsubscribe']
  """Which request this acknowledges."""
  subscription: dict[str, Any]
  """The subscription, echoed back."""


class SubscriptionResponse(TypedDict):
  """A subscribe/unsubscribe ack."""

  channel: Literal['subscriptionResponse']
  """The ack tag."""
  data: SubscriptionResponseData
  """The request acknowledged."""


class ErrorFrame(TypedDict):
  """A refused request (or any other server-side error)."""

  channel: Literal['error']
  """The error tag."""
  data: Any
  """The error message; a refusal quotes the raw request it refuses."""


class Push(TypedDict):
  """Any other frame: a push on a subscribed channel (or a `pong`)."""

  channel: str
  """The push tag (`l2Book`, `trades`, ..., `pong`)."""
  data: Any
  """The payload a stream yields."""


Reply = SubscriptionResponse | ErrorFrame
"""What answers a subscribe/unsubscribe request: an ack or a refusal."""
validate_frame = validator(Push)
"""Checks a decoded frame is `{channel, data}` before it is routed."""


def without_nulls(subscription: Mapping[str, Any]) -> dict[str, Any]:
  """`subscription` without `None` values, which are never sent."""
  return {k: v for k, v in subscription.items() if v is not None}


@dataclass
class PendingRequest:
  """The one subscribe/unsubscribe request awaiting its reply."""

  method: Literal['subscribe', 'unsubscribe']
  """The request's `method`."""
  subscription: Mapping[str, Any]
  """The request's `subscription`, as sent."""
  raw: str
  """The request exactly as written to the wire (refusals quote it)."""
  reply: 'asyncio.Future[Reply]'
  """Resolved by `parse_msg` with the reply tied to this request."""

  def answered_by(self, frame: Push) -> bool:
    """Whether `frame` (an ack or a refusal) answers this request.

    An ack answers it when it echoes this `method` and, if it echoes a `subscription` at all,
    this one (an ack echoing none is left to the reply validator to refuse). A refusal answers
    it when its message quotes this request's raw text, as the venue's refusals do.
    """
    data = frame['data']
    if frame['channel'] == 'error':
      return isinstance(data, str) and self.raw in data
    elif not isinstance(data, Mapping) or data.get('method') != self.method:
      return False
    elif (echoed := data.get('subscription')) is None:
      return True
    else:
      return isinstance(echoed, Mapping) and without_nulls(echoed) == without_nulls(
        self.subscription
      )


@dataclass
class SocketConnection(
  Streams[Any, Params, SubscriptionResponseData, SubscriptionResponseData],
):
  """One `/ws` connection, multiplexing every subscription.

  `timeout` bounds both the handshake and the wait for each subscribe/unsubscribe reply.
  """

  ping_interval: timedelta = field(kw_only=True, default=timedelta(seconds=30))
  """How often the protocol-level `{"method": "ping"}` is sent."""
  pending: PendingRequest | None = field(default=None, init=False, repr=False)
  """The request in flight, if any."""
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  """Serializes subscribe/unsubscribe requests: replies carry no id."""

  async def send(self, msg: object):
    """Write one JSON frame.

    Raises:
      NetworkError: The connection failed while sending.
    """
    await self.send_raw(json.dumps(msg, separators=(',', ':')))

  async def send_raw(self, raw: str):
    """Write one already-encoded text frame.

    Raises:
      NetworkError: The connection failed while sending.
    """
    ws = await self.ws
    try:
      await ws.send(raw, text=True)
    except websockets.exceptions.WebSocketException as e:
      raise NetworkError('Error sending message', type(e).__name__) from e

  async def ping(self, ws: websockets.ClientConnection):
    """Send the protocol-level ping; the `pong` reply is dropped in `parse_msg`."""
    await ws.send(json.dumps({'method': 'ping'}), text=True)

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    """Route a reply to the request it answers, a push to its subscription; log and drop
    anything else, so one bad frame never ends the shared connection.
    """
    try:
      frame = validate_frame.python(json.loads(msg))
    except (ValueError, ValidationError):
      logger.warning('Dropping a frame that is not {channel, data}: %.200r', msg)
    else:
      return self.route(frame)

  def route(self, frame: Push) -> Subscription[Any] | None:
    """Resolve the request in flight with the reply `frame` answers (dropping a reply it does
    not), or hand a push to its subscription; `pong`s go nowhere.
    """
    channel = frame['channel']
    if channel == 'subscriptionResponse' or channel == 'error':
      pending = self.pending
      if (
        pending is not None and not pending.reply.done() and pending.answered_by(frame)
      ):
        pending.reply.set_result(cast(Reply, frame))
      else:
        logger.warning('Dropping a reply to no request in flight: %.200r', frame)
    elif channel != 'pong':
      return {'channel': channel, 'notification': frame['data']}

  async def subscription_request(
    self, method: Literal['subscribe', 'unsubscribe'], params: Params | None
  ) -> SubscriptionResponseData:
    """Send one subscribe/unsubscribe request and return its ack.

    A subscribe that times out or is cancelled may still be applied by the server (its ack
    arriving late, or never), so it is followed by a best-effort unsubscribe of the same
    `subscription`, sent without waiting for its ack, so the server stops pushing.

    Raises:
      BadRequest: The server refused it.
      NetworkError: No reply tied to it arrived within `timeout`, or the connection failed.
    """
    subscription = params['subscription'] if params else {}
    raw = json.dumps(
      {'method': method, 'subscription': subscription}, separators=(',', ':')
    )
    async with self.lock:
      future = asyncio.get_running_loop().create_future()
      self.pending = PendingRequest(method, subscription, raw, future)
      try:
        await self.send_raw(raw)
        reply = await asyncio.wait_for(future, self.timeout.total_seconds())
      except asyncio.TimeoutError as e:
        await self.undo_subscribe(method, subscription)
        raise NetworkError(f'No reply to "{method}" within {self.timeout}', raw) from e
      except asyncio.CancelledError:
        await self.undo_subscribe(method, subscription)
        raise
      finally:
        self.pending = None
    if reply['channel'] == 'error':
      raise BadRequest(reply['data'], reply)
    else:
      return reply['data']

  async def undo_subscribe(
    self, method: Literal['subscribe', 'unsubscribe'], subscription: Mapping[str, Any]
  ):
    """After an unanswered `subscribe`, send its unsubscribe (best effort, bounded by
    `timeout`, ack not awaited: a late one is dropped like any reply to no request in
    flight). Nothing to undo after an unanswered `unsubscribe`.
    """
    if method != 'subscribe':
      return
    msg = {'method': 'unsubscribe', 'subscription': subscription}
    try:
      await asyncio.wait_for(self.send(msg), self.timeout.total_seconds())
    except Exception:
      logger.warning(
        'Unsubscribing after an unanswered subscribe failed', exc_info=True
      )

  async def request_subscription(
    self, channel: str, params: Params | None = None
  ) -> SubscriptionResponseData:
    """Subscribe; `channel` is the push tag, the wire request is `params['subscription']`."""
    return await self.subscription_request('subscribe', params)

  async def request_unsubscription(
    self, channel: str, params: Params | None = None
  ) -> SubscriptionResponseData:
    """Unsubscribe with the identical `subscription` object."""
    return await self.subscription_request('unsubscribe', params)


@dataclass(kw_only=True)
class SocketClient(StreamClient):
  """WebSocket client, owning the connection and push validation."""

  conn: SocketConnection
  """The one `/ws` connection."""
  validate: bool = True
  """Validate pushes by default."""

  @classmethod
  def new(
    cls,
    url: str,
    *,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    ping_interval: timedelta = timedelta(seconds=30),
  ) -> 'SocketClient':
    """Build the transport for one network's WebSocket URL (connects lazily)."""
    conn = SocketConnection(url=url, timeout=timeout, ping_interval=ping_interval)
    return cls(conn=conn, validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self):
    """Take ownership of the connection without connecting."""
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection, if it was opened."""
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    subscription: Mapping[str, Any],
    *,
    channel: str | None = None,
    route: Mapping[str, str] | None = None,
    validator: validator[T] | None = None,
    reply_validator: validator[R] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, R, Any]:
    """Subscribe with `subscription`, routing its pushes by `route` (see `StreamMeta`), and
    validating the acknowledgement's `data` with `reply_validator`.
    """
    tag = channel or subscription['type']
    paths = dict(route or {})
    key = route_key(tag, {name: subscription.get(name) for name in paths})

    def message_key(data: Any) -> str:
      """The local key a push on `tag` belongs to."""
      return route_key(tag, {name: resolve(data, path) for name, path in paths.items()})

    manager = self.conn.subscribe(
      key,
      {'subscription': subscription},
      request_channel=tag,
      message_key=message_key if paths else None,
    )
    if not self.should_validate(validate):
      return cast(StreamManager[T, R, Any], manager)
    if reply_validator is not None:
      connect = manager.connect

      async def validated_connect():
        """Connect, then validate the acknowledgement.

        Raises:
          ValidationError: The acknowledgement does not match its type; the subscription
            just made is dropped first (best effort), so a retry can subscribe again.
        """
        stream = await connect()
        try:
          reply = reply_validator.python(stream.reply)
        except BaseException:
          try:
            await stream.unsubscribe()
          except Exception:
            logger.warning(
              'Unsubscribing after a refused acknowledgement failed', exc_info=True
            )
          raise
        return replace(stream, reply=reply)

      manager = StreamManager(connect=validated_connect)
    if validator is not None:
      return cast(StreamManager[T, R, Any], manager.map(validator))
    else:
      return cast(StreamManager[T, R, Any], manager)
