"""WebSocket transport: channel subscriptions and `jsonapi/sendtx` RPC on one `/stream` connection.

Wire protocol (verified live on testnet, 2026-09-24):

- On connect the server sends `{"type": "connected", "session_id": ...}`.
- Subscribe with `{"type": "subscribe", "channel": "order_book/0"[, "auth": token]}`. The
  first reply is a `subscribed/<kind>` snapshot and later pushes are `update/<kind>`; both
  label the channel in colon form (`order_book:0`), so the colon form is the local routing
  key and the slash form is what gets sent. `account_orders` is the exception: its frames
  (and its unsubscribe ack) say `account_orders:<market>` without the account, which is
  only in the frame body (`routing_channel`).
- Unsubscribe acks with `{"type": "unsubscribed", "channel": "<colon form>"}`.
- Subscription errors are `{"error": {"code", "message"}}` with no type, channel or id. Some
  messages end with the colon channel (`auth field is required: account_all_orders:476`),
  others do not (`Invalid Channel`), and acks for concurrent subscribes can arrive out of
  send order. Subscribe/unsubscribe requests are therefore serialized per connection, so
  an error naming no channel can only belong to the one request in flight.
- RPC frames `{"type": "jsonapi/sendtx", "data": {"id": ..., ...}}` get a reply echoing `id`
  at the top level; errors are `{"error": {...}, "id": ...}`, and a reply whose top-level
  `code` is not `200` is mapped exactly as an HTTP body's is.
- The client must send something at least every 2 minutes: `{"type": "ping"}` gets
  `{"type": "pong"}`. A server `{"type": "ping"}` is answered with `{"type": "pong"}`.

Dropped connections follow `typed_core.ws` (0.9.2+): a stream on a dropped connection raises
`NetworkError` (after delivering what it already received), an in-flight RPC raises
`NetworkError`, leaving a stream whose connection is gone sends nothing, and the next
subscribe or RPC opens a fresh connection. Nothing is resubscribed automatically.
"""

from typing_extensions import Any, Literal, NotRequired, Self, TypeVar, TypedDict
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json
import logging

from typed_core.util import StreamManager
from typed_core.validation import validator
from typed_core.ws import StreamsRpc
from typed_core.ws.socket import Context
from typed_core.ws.streams_rpc import Message
import websockets

from ..auth import TokenProvider
from ..endpoint.stream import StreamClient
from ..envelope import CODE_OK, parse_code, raise_code, raise_error_frame
from ..exc import ApiError, AuthError, NetworkError
from ..signer.txs.base import TxInfo

T = TypeVar('T')

logger = logging.getLogger(__name__)

PING_INTERVAL = timedelta(seconds=60)
"""Client keepalive period; the server drops connections idle for 2 minutes."""


class SubscribeParams(TypedDict):
  """Local subscription options, resolved into the subscribe frame."""

  authed: bool
  """Attach an auth token to the subscribe frame."""


class SendTxData(TypedDict):
  """`jsonapi/sendtx`'s `data`: one signed transaction."""

  tx_type: int
  """Lighter transaction type id."""
  tx_info: TxInfo
  """The signed transaction body, as a JSON object (not the string `sendTx` takes)."""


class SendTxFrame(TypedDict):
  """A `jsonapi/sendtx` frame before its correlation id is added."""

  type: Literal['jsonapi/sendtx']
  """Frame type."""
  data: SendTxData
  """The transaction."""


class SendTxBatchData(TypedDict):
  """`jsonapi/sendtxbatch`'s `data`: signed transactions, as JSON-encoded arrays."""

  tx_types: str
  """JSON array of the transactions' type ids."""
  tx_infos: str
  """JSON array of the transactions' `tx_info` strings."""


class SendTxBatchFrame(TypedDict):
  """A `jsonapi/sendtxbatch` frame before its correlation id is added."""

  type: Literal['jsonapi/sendtxbatch']
  """Frame type."""
  data: SendTxBatchData
  """The transactions."""


RpcRequest = SendTxFrame | SendTxBatchFrame
"""One RPC frame before its correlation id is added."""


class SubscribeFrame(TypedDict):
  """A channel subscribe request."""

  type: Literal['subscribe']
  """Frame type."""
  channel: str
  """Slash-form channel (`order_book/0`)."""
  auth: NotRequired[str]
  """Auth token, for a private channel."""


class UnsubscribeFrame(TypedDict):
  """A channel unsubscribe request."""

  type: Literal['unsubscribe']
  """Frame type."""
  channel: str
  """Slash-form channel."""


def colon(channel: str) -> str:
  """The colon form the server labels a slash-form channel with (`order_book/0` -> `order_book:0`)."""
  return channel.replace('/', ':')


def routing_channel(frame: dict[str, Any]) -> str | None:
  """The colon-form channel a pushed frame belongs to.

  `account_orders/{market}/{account}` frames are labelled `account_orders:{market}`, with
  the account only in the body (`account`), so the account is appended back to route them.
  """
  channel = frame.get('channel')
  if (
    isinstance(channel, str)
    and channel.startswith('account_orders:')
    and channel.count(':') == 1
    and 'account' in frame
  ):
    return f'{channel}:{frame["account"]}'
  return channel


@dataclass
class SocketConnection(
  StreamsRpc[RpcRequest, Any, Any, SubscribeParams, Any, Any],
):
  """One `/stream` connection: subscriptions, keepalive and id-correlated RPC."""

  tokens: TokenProvider | None = None
  """Auth token source for private channels; `None` for public-only use."""
  pending: dict[str, asyncio.Future[Any]] = field(
    default_factory=dict, init=False, repr=False
  )
  """In-flight subscribe/unsubscribe request, by colon channel (at most one at a time)."""
  exchange_lock: asyncio.Lock = field(
    default_factory=asyncio.Lock, init=False, repr=False
  )
  """Serializes subscribe/unsubscribe requests so channel-less errors stay attributable."""
  tasks: set[asyncio.Task] = field(default_factory=set, init=False, repr=False)
  """Pong replies still being sent, kept referenced until they finish."""

  def connection_closed(self, ctx: Context):
    """Fail the closed connection's in-flight subscribe/unsubscribe request."""
    for future in self.pending.values():
      if not future.done():
        future.set_exception(NetworkError('WebSocket connection closed'))
        future.exception()
    self.pending.clear()
    super().connection_closed(ctx)

  async def send(self, msg: object):
    """Write one JSON frame on the current (or bound) connection.

    Raises:
      NetworkError: The connection closed while sending.
    """
    ws = await self.ws
    try:
      await ws.send(json.dumps(msg))
    except websockets.exceptions.ConnectionClosed as e:
      raise NetworkError('WebSocket connection closed') from e

  async def ping(self, ws: websockets.ClientConnection):
    """Keep the connection alive with Lighter's application-level ping."""
    await ws.send(json.dumps({'type': 'ping'}))

  def pong(self):
    """Answer a server ping on the live connection, from the synchronous message handler."""
    future = self._ctx_future
    if future is None or not future.done() or future.cancelled() or future.exception():
      return
    ctx = future.result()
    if not ctx.alive:
      return

    async def answer():
      """Send the pong; a connection closing meanwhile is reported by its listener."""
      try:
        await ctx.ws.send(json.dumps({'type': 'pong'}))
      except websockets.exceptions.ConnectionClosed:
        pass

    task = asyncio.ensure_future(answer())
    self.tasks.add(task)
    task.add_done_callback(self.tasks.discard)

  def settle(
    self, channel: str | None, *, result: Any = None, error: BaseException | None = None
  ):
    """Resolve the pending request for `channel`, or the one in flight when `channel` is unknown."""
    if channel is None or channel not in self.pending:
      if not self.pending:
        if error is not None:
          logger.warning('Unattributed WebSocket error: %s', error)
        return
      channel = next(iter(self.pending))
    future = self.pending.pop(channel)
    if future.done():
      return
    if error is not None:
      future.set_exception(error)
    else:
      future.set_result(result)

  def error_channel(self, message: str) -> str | None:
    """The pending channel an error message names, if it names one."""
    for channel in self.pending:
      if message.endswith(channel):
        return channel
    return None

  def parse_msg(self, msg: str | bytes, /) -> Message[Any, Any] | None:
    """Route one incoming frame: an RPC reply (by `id`), a subscription push, or a
    control frame (error, ping, unsubscribe ack) handled here and dropped.

    Args:
      msg: The raw frame.
    """
    obj = json.loads(msg)
    if 'id' in obj:
      try:
        id = int(obj['id'])
      except (TypeError, ValueError):
        return None
      if id not in self.replies:
        return None
      return {'kind': 'response', 'id': id, 'response': obj}
    if (error := obj.get('error')) is not None:
      try:
        raise_error_frame(error, obj)
      except ApiError as e:
        self.settle(self.error_channel(str(e.args[1])), error=e)
      return None
    kind = obj.get('type', '')
    if kind == 'ping':
      self.pong()
      return None
    if kind == 'unsubscribed':
      self.settle(obj.get('channel'), result=obj)
      return None
    if kind.startswith('subscribed/') or kind.startswith('update/'):
      channel = routing_channel(obj)
      if kind.startswith('subscribed/'):
        self.settle(channel, result=obj)
      if channel is not None:
        return {'kind': 'subscription', 'channel': channel, 'notification': obj}
    return None

  async def rpc_send(self, id: int, req: RpcRequest, /):
    """Send one RPC frame, its correlation id as a string inside `data`.

    Args:
      id: Correlation id.
      req: The frame, without its id.
    """
    await self.send({'type': req['type'], 'data': {'id': str(id), **req['data']}})

  async def exchange(
    self, channel: str, frame: SubscribeFrame | UnsubscribeFrame
  ) -> Any:
    """Send a subscribe/unsubscribe frame and await its ack (or mapped error).

    Args:
      channel: Slash-form channel.
      frame: The frame to send.
    """
    key = colon(channel)
    async with self.exchange_lock:
      future = asyncio.get_running_loop().create_future()
      self.pending[key] = future
      try:
        await self.send(frame)
        return await asyncio.wait_for(future, self.timeout.total_seconds())
      finally:
        if self.pending.get(key) is future:
          del self.pending[key]

  async def request_subscription(
    self, channel: str, params: SubscribeParams | None = None
  ) -> Any:
    """Subscribe to a slash-form channel, with an auth token when `params` asks for one.

    Args:
      channel: Slash-form channel.
      params: Local subscription options.

    Raises:
      AuthError: The channel needs a token and the client has no credentials.
    """
    frame: SubscribeFrame = {'type': 'subscribe', 'channel': channel}
    if params is not None and params['authed']:
      if self.tokens is None:
        raise AuthError(
          'This channel needs an auth token: build the client with credentials.'
        )
      frame['auth'] = self.tokens.token()
    return await self.exchange(channel, frame)

  async def request_unsubscription(
    self, channel: str, params: SubscribeParams | None = None
  ) -> Any:
    """Unsubscribe from a slash-form channel and await the ack.

    Args:
      channel: Slash-form channel.
      params: Local subscription options (unused: unsubscribing needs no token).
    """
    return await self.exchange(channel, {'type': 'unsubscribe', 'channel': channel})


@dataclass(kw_only=True)
class SocketClient(StreamClient):
  """WebSocket client backing `client.streams` and `client.tx`'s `transport='ws'`."""

  conn: SocketConnection
  """The one `/stream` connection."""
  validate: bool = True
  """Validate responses and pushes by default."""

  @classmethod
  def new(
    cls,
    url: str,
    *,
    tokens: TokenProvider | None = None,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    ping_interval: timedelta = PING_INTERVAL,
  ) -> 'SocketClient':
    """Build the client for one `/stream` URL; connects lazily on first use."""
    conn = SocketConnection(
      url, tokens=tokens, timeout=timeout, ping_interval=ping_interval
    )
    return cls(conn=conn, validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    """Take ownership of the `/stream` connection without connecting (it opens lazily)."""
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the `/stream` connection, if it was opened, ending every live subscription on
    it. Only the root client (`core.client.ClientBase`) calls this."""
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    *,
    authed: bool = False,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to `channel` (slash form); the stream yields the snapshot, then every update."""
    manager = self.conn.subscribe(
      colon(channel), {'authed': authed}, request_channel=channel
    )
    if validator is None or not self.should_validate(validate):
      return manager
    return manager.map(validator)

  async def rpc(
    self,
    request: RpcRequest,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one RPC frame, raise on an error reply, then validate.

    A reply is an error when it carries `{"error": {code, message}}`, or, as over HTTP
    (`core.envelope.unwrap`), a top-level `code` other than `200`; both raise whether or
    not the reply is validated.

    The whole call (connecting if needed, sending, awaiting the reply) is bounded by the
    connection's `timeout`, the same one subscribe/unsubscribe acks use. A frame the
    server never answers raises `NetworkError` and its pending reply is discarded; the
    transaction may still have landed, so callers treat it as an unknown outcome.

    Raises:
      ApiError: The reply carried an `error`, or a top-level `code` other than `200` (the
        subclass `raise_code` maps it to).
      NetworkError: The connection dropped, or no reply arrived within `timeout`.
    """
    seconds = self.conn.timeout.total_seconds()
    try:
      reply = await asyncio.wait_for(self.conn.rpc_request(request), seconds)
    except asyncio.TimeoutError as e:
      raise NetworkError(
        f'No reply to {request["type"]} within {seconds:g}s; outcome unknown'
      ) from e
    if (error := reply.get('error')) is not None:
      raise_error_frame(error, reply)
    if (code := parse_code(reply.get('code'))) is not None and code != CODE_OK:
      raise_code(code, str(reply.get('message', '')), reply)
    if validator is not None and self.should_validate(validate):
      return validator.python(reply)
    return reply
