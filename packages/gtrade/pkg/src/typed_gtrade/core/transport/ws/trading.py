"""Trading API WebSocket transport, `wss://api.gains.trade/v1/{chain}/ws`: one connection
per chain carrying every channel.

Wire protocol, as observed live:

- The server greets with `{"op": "hello", "heartbeatMs": 15000}`, pings every 15 s, and
  closes a connection that sends nothing for about a minute (close code 4000, "idle"),
  so the transport sends `{"op": "ping"}` every 15 s.
- `{"op": "subscribe" | "unsubscribe", "channel", ...keys}` is acknowledged by
  `{"op": "subscribed" | "unsubscribed", "channel", ...keys}`, rejected by
  `{"op": "error", "code", "message"}`. The snapshot frame arrives *before* the ack.
- Data frames are `{"channel", ...keys, "snapshot", "seq"?, "data"}`; a market key is
  echoed `BTC/USD` even when subscribed as `BTC-USD`.
- `{"op": "auth", ...}` is answered by `{"op": "authenticated", "trader", "via"}` or an
  error. One auth per connection covers every private channel on it.

Replies carry no request id, and an error frame names nothing at all, so one request is
on the wire at a time (`TradingSocket.request`) and the frame answering it is recognized
by what it acknowledges: its `op`, channel and echoed keys, or any error frame. A reply
that answers nothing in flight is dropped, never queued for the next request. A caller
that stops waiting (cancelled) does not end its request: the request keeps the wire
until its reply or the reply timeout, so the next one can never read it, and a
subscription acknowledged after its caller left is unsubscribed at once (the venue caps a
connection at 200 subscriptions). The same holds for a subscription acknowledged after
its reply timeout.
"""

from typing_extensions import Any, Literal, Mapping, TypedDict, TypeVar, cast
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json
import logging

import httpx
import websockets

from typed_core.util import StreamManager
from typed_core.validation import validator
from typed_core.ws import Streams
from typed_core.ws.socket import Context
from typed_core.ws.streams import Subscription

from ...auth import AgentSigner
from ...endpoint.trading_streams import TradingStreamClient
from ...envelope import raise_code
from ...exc import AuthError, NetworkError

T = TypeVar('T')

logger = logging.getLogger(__name__)

PING_INTERVAL = timedelta(seconds=15)
"""The server's own heartbeat period; it drops a client silent for about a minute."""

REPLY_TIMEOUT = timedelta(seconds=10)
"""How long a subscribe, unsubscribe or `auth` frame waits for its reply by default."""

KEY_FIELDS = ('market', 'interval')
"""The keys a data frame echoes, in the order they enter its routing key."""

REPLY_OPS = frozenset({'subscribed', 'unsubscribed', 'authenticated', 'error'})
"""Control frames answering a request."""

Frame = dict[str, Any]
"""One decoded JSON frame."""


class SubscribeParams(TypedDict):
  """What one subscription sends: its keys, and whether it needs the connection authenticated."""

  keys: dict[str, Any]
  private: bool


def key_value(field: str, value: Any) -> str:
  """One key as it enters a routing key: markets in their echoed `BTC/USD` form."""
  text = str(value)
  return text.replace('-', '/') if field == 'market' else text


def routing_key(channel: str, keys: Mapping[str, Any]) -> str:
  """The local identity of a subscription, and of every data frame it receives:
  `book|BTC/USD`, `candles|BTC/USD|1m`, `prices`."""
  parts = [channel]
  parts.extend(
    key_value(name, keys[name]) for name in KEY_FIELDS if keys.get(name) is not None
  )
  return '|'.join(parts)


def consume(task: 'asyncio.Future[Any]'):
  """Retrieve a background task's outcome, so the failure of a request whose caller left
  is never reported as unretrieved (a failed orphan unsubscribe logs its own warning)."""
  if not task.cancelled():
    task.exception()


def raise_error(reply: Frame):
  """Raise the error a reply carries, if it is an error frame.

  Raises:
    AuthError, RateLimited, BadRequest, ApiError: `reply` is `{"op": "error", ...}`.
  """
  if reply.get('op') == 'error':
    raise_code(
      code=str(reply.get('code')), message=str(reply.get('message')), payload=reply
    )


@dataclass(eq=False)
class Request:
  """One request on the wire: the acknowledgement that answers it, and where it lands."""

  frame: Frame
  """What is sent."""
  ack: str
  """The `op` acknowledging it: `subscribed`, `unsubscribed` or `authenticated`."""
  channel: str | None = None
  """The channel a subscribe or unsubscribe names; `None` for `auth`."""
  keys: Mapping[str, Any] = field(default_factory=dict)
  """The channel keys as sent."""
  ctx: Context | None = field(default=None, repr=False)
  """The connection it is on, once sent."""
  reply: 'asyncio.Future[Frame] | None' = field(default=None, repr=False)
  """Resolved with the frame answering it, once sent."""
  abandoned: bool = False
  """Whether its caller stopped waiting before the reply arrived."""

  @classmethod
  def subscription(
    cls,
    *,
    op: Literal['subscribe', 'unsubscribe'],
    channel: str,
    keys: Mapping[str, Any],
  ) -> 'Request':
    """A `subscribe` or `unsubscribe` request."""
    return cls(
      frame={'op': op, 'channel': channel, **keys},
      ack=f'{op}d',
      channel=channel,
      keys=keys,
    )

  @property
  def key(self) -> str | None:
    """The routing key of the subscription it names; `None` for `auth`."""
    return None if self.channel is None else routing_key(self.channel, self.keys)

  def answered_by(self, frame: Frame) -> bool:
    """Whether `frame` answers this request: any error frame (they name no request), or
    this request's acknowledgement, for its channel and with every key it echoes equal
    to the one sent (markets compared in their `BTC/USD` form)."""
    if frame.get('op') == 'error':
      return True
    if frame.get('op') != self.ack:
      return False
    if self.channel is None:
      return True
    if frame.get('channel') != self.channel:
      return False
    return all(
      key_value(name, frame[name]) == key_value(name, self.keys.get(name))
      for name in KEY_FIELDS
      if frame.get(name) is not None
    )


@dataclass
class TradingSocket(Streams[Frame, SubscribeParams, Frame, Frame]):
  """One Trading API WebSocket connection: subscriptions, the auth handshake and heartbeats."""

  ping_interval: timedelta = field(kw_only=True, default=PING_INTERVAL)
  reply_timeout: timedelta = field(kw_only=True, default=REPLY_TIMEOUT)
  """How long a request waits for its reply before raising `NetworkError`."""
  signer: AgentSigner | None = field(kw_only=True, default=None)
  """Signs the `auth` frame when there is no API key."""
  api_key: str | None = field(kw_only=True, default=None, repr=False)
  """Authenticates the connection on its own (private channels are read-only)."""
  authenticated: bool = field(default=False, init=False, repr=False)
  """Whether the current connection has authenticated."""
  auth_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  wire_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  """Held by the request on the wire, until its reply or its timeout."""
  in_flight: Request | None = field(default=None, init=False, repr=False)
  """The request awaiting its reply, if any."""
  timed_out: dict[str, Mapping[str, Any]] = field(
    default_factory=dict, init=False, repr=False
  )
  """The keys sent by each subscribe request whose reply timed out on the current
  connection, by routing key: a late acknowledgement of one is unsubscribed."""

  @property
  def auth_path(self) -> str:
    """The path the `auth` signature names: the connection's own, `/v1/{chain}/ws`."""
    return httpx.URL(self.url).path

  async def ping(self, ws: websockets.ClientConnection):
    """Keep the connection from being closed as idle."""
    await ws.send('{"op":"ping"}')

  def connection_closed(self, ctx: Context):
    """A new connection has to authenticate again, and nothing awaits a reply from a
    closed one."""
    self.authenticated = False
    self.timed_out.clear()
    request = self.in_flight
    if (
      request is not None
      and request.ctx is ctx
      and request.reply is not None
      and not request.reply.done()
    ):
      request.reply.set_exception(NetworkError('WebSocket connection closed'))
      request.reply.exception()  # retrieved by its waiter, if any
    super().connection_closed(ctx)

  def parse_msg(self, msg: str | bytes) -> Subscription[Frame] | None:
    """Route a data frame to its subscription and a reply to the request it answers."""
    try:
      obj = json.loads(msg)
    except ValueError:
      logger.warning('Dropping a non-JSON frame: %.200r', msg)
      return None
    if not isinstance(obj, dict):
      return None
    op = obj.get('op')
    if op is None:
      channel = obj.get('channel')
      if isinstance(channel, str) and 'data' in obj:
        return {'channel': routing_key(channel, obj), 'notification': obj}
      return None
    if op in REPLY_OPS:
      self.on_reply(obj)
    return None

  def on_reply(self, frame: Frame):
    """Hand a reply to the request it answers, or drop it.

    A `subscribed` answering nothing in flight, for a subscribe whose reply timed out,
    is unsubscribed in the background: nobody holds that subscription.
    """
    request = self.in_flight
    if (
      request is not None
      and request.reply is not None
      and not request.reply.done()
      and request.answered_by(frame)
    ):
      if frame.get('op') == 'authenticated':
        self.authenticated = True
      request.reply.set_result(frame)
      return
    if frame.get('op') == 'subscribed' and isinstance(frame.get('channel'), str):
      keys = self.timed_out.pop(routing_key(frame['channel'], frame), None)
      ctx = self.current_ctx()
      if keys is not None and ctx is not None:
        task = asyncio.ensure_future(
          self.unsubscribe_orphan(ctx, frame['channel'], keys)
        )
        task.add_done_callback(consume)
        return
    logger.warning('Dropping a reply no request is waiting for: %.200s', frame)

  def current_ctx(self) -> Context | None:
    """The open connection, without connecting; `None` when there is none."""
    # Reads typed_core's private `Socket._ctx_future` (typed-core 0.14.0): the public
    # `ctx`/`ctx_future` would connect or create a future. Check it on a typed-core
    # upgrade, until typed-core exposes a non-connecting accessor.
    future = self._ctx_future
    if (
      future is None
      or not future.done()
      or future.cancelled()
      or future.exception() is not None
    ):
      return None
    ctx = future.result()
    return ctx if ctx.alive else None

  async def exchange(self, ctx: Context, request: Request) -> Frame:
    """Send `request` on `ctx` and wait for the frame answering it. The caller holds
    `wire_lock`.

    Raises:
      NetworkError: The connection is gone, or no reply arrived within `reply_timeout`.
    """
    if not ctx.alive:
      raise ctx.failure()
    request.ctx = ctx
    request.reply = asyncio.get_running_loop().create_future()
    self.in_flight = request
    try:
      try:
        await ctx.ws.send(json.dumps(request.frame, separators=(',', ':')))
      except websockets.exceptions.WebSocketException as error:
        raise NetworkError('Error sending a request') from error
      try:
        return await asyncio.wait_for(
          self.wait(asyncio.shield(request.reply), ctx=ctx),
          self.reply_timeout.total_seconds(),
        )
      except asyncio.TimeoutError:
        if request.ack == 'subscribed' and request.key is not None and ctx.alive:
          self.timed_out[request.key] = request.keys
        raise NetworkError(
          f'No reply to {request.frame.get("op")!r}'
          + (f' for {request.key!r}' if request.key is not None else '')
          + f' within {self.reply_timeout.total_seconds():g} s'
        ) from None
    finally:
      if self.in_flight is request:
        self.in_flight = None

  async def transact(self, ctx: Context, request: Request) -> Frame:
    """Hold the wire for `request` until its reply, then, if its caller left before a
    `subscribed` arrived, unsubscribe before anything else is sent. A request whose caller
    left while it waited for the wire is never sent."""
    async with self.wire_lock:
      if request.abandoned:
        raise asyncio.CancelledError
      reply = await self.exchange(ctx, request)
      if request.abandoned and reply.get('op') == 'subscribed':
        await self.unsubscribe_now(ctx, request.channel, request.keys)
      return reply

  async def request(self, request: Request) -> Frame:
    """Send `request` and return the frame answering it: its acknowledgement, or an
    error frame. Serialized against every other request on the connection.

    Cancellation-safe: a cancelled caller leaves the request to finish in the background
    (see `transact`), so its reply never answers a later request.

    Raises:
      NetworkError: The connection is gone, or no reply arrived within `reply_timeout`.
    """
    # Inside `Streams.wait`, the connection the subscription was made on.
    ctx = await self.ctx
    if request.ack == 'subscribed' and request.key is not None:
      # A fresh subscription supersedes a timed-out one for the same key.
      self.timed_out.pop(request.key, None)
    task = asyncio.ensure_future(self.transact(ctx, request))
    task.add_done_callback(consume)
    try:
      return await asyncio.shield(task)
    except asyncio.CancelledError:
      request.abandoned = True
      if (
        task.done()
        and not task.cancelled()
        and task.exception() is None
        and task.result().get('op') == 'subscribed'
      ):
        # Acknowledged just before the cancellation reached the caller, which will
        # never see it: nobody holds that subscription.
        orphan = asyncio.ensure_future(
          self.unsubscribe_orphan(ctx, request.channel, request.keys)
        )
        orphan.add_done_callback(consume)
      raise

  async def unsubscribe_now(
    self, ctx: Context, channel: str | None, keys: Mapping[str, Any]
  ):
    """Unsubscribe a server-side subscription nobody holds, logging any failure. The
    caller holds `wire_lock`."""
    if channel is None:
      return
    try:
      reply = await self.exchange(
        ctx, Request.subscription(op='unsubscribe', channel=channel, keys=keys)
      )
    except NetworkError as error:
      logger.warning('Could not unsubscribe an orphaned %r: %s', channel, error)
      return
    if reply.get('op') == 'error':
      logger.warning('Could not unsubscribe an orphaned %r: %s', channel, reply)

  async def unsubscribe_orphan(
    self, ctx: Context, channel: str | None, keys: Mapping[str, Any]
  ):
    """Unsubscribe a server-side subscription acknowledged after its request was
    released, unless the same subscription has been made again locally meanwhile (the
    server-side one then serves it)."""
    if channel is None:
      return
    async with self.wire_lock:
      if not ctx.alive or routing_key(channel, keys) in self.subscriptions:
        return
      await self.unsubscribe_now(ctx, channel, keys)

  def auth_frame(self) -> dict[str, str]:
    """The `auth` frame: the API key when there is one, else the agent signature.

    Raises:
      AuthError: The client has neither.
    """
    if self.api_key is not None:
      return {'op': 'auth', 'apiKey': self.api_key}
    if self.signer is not None:
      return self.signer.ws_auth(self.auth_path)
    raise AuthError(
      'Private channels need an API key or an agent key: build the client with '
      '`api_key` or `agent` (not `public=True`).'
    )

  async def authenticate(self):
    """Authenticate the current connection, once.

    Raises:
      AuthError: No credential, or the server rejected it.
      NetworkError: No reply within `reply_timeout`.
    """
    async with self.auth_lock:
      if self.authenticated:
        return
      raise_error(await self.request(Request(self.auth_frame(), 'authenticated')))

  async def request_subscription(
    self, channel: str, params: SubscribeParams | None = None
  ) -> Frame:
    """Subscribe, authenticating the connection first for a private channel.

    Raises:
      AuthError, RateLimited, BadRequest, ApiError: The server refused it.
      NetworkError: No reply within `reply_timeout`.
    """
    params = params or {'keys': {}, 'private': False}
    if params['private']:
      await self.authenticate()
    reply = await self.request(
      Request.subscription(op='subscribe', channel=channel, keys=params['keys'])
    )
    raise_error(reply)
    return reply

  async def request_unsubscription(
    self, channel: str, params: SubscribeParams | None = None
  ) -> Frame:
    """Unsubscribe.

    Raises:
      AuthError, RateLimited, BadRequest, ApiError: The server refused it.
      NetworkError: No reply within `reply_timeout`.
    """
    keys = params['keys'] if params else {}
    reply = await self.request(
      Request.subscription(op='unsubscribe', channel=channel, keys=keys)
    )
    raise_error(reply)
    return reply


@dataclass(kw_only=True)
class TradingSocketClient(TradingStreamClient):
  """`TradingStreamClient` over one `TradingSocket`, owning frame validation."""

  socket: TradingSocket
  validate: bool = True

  @classmethod
  def new(
    cls,
    url: str,
    *,
    signer: AgentSigner | None = None,
    api_key: str | None = None,
    validate: bool = True,
    timeout: timedelta = REPLY_TIMEOUT,
  ):
    """Build the transport for one chain's WebSocket URL.

    Args:
      url: The chain's WebSocket URL.
      signer: Signs the `auth` frame when there is no API key.
      api_key: Authenticates private channels on its own.
      validate: Validate data frames by default.
      timeout: Of the connection handshake, and of each request's reply.
    """
    socket = TradingSocket(
      url, signer=signer, api_key=api_key, timeout=timeout, reply_timeout=timeout
    )
    return cls(socket=socket, validate=validate)

  async def __aenter__(self):
    await self.socket.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.socket.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    keys: Mapping[str, Any] | None = None,
    *,
    private: bool = False,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to one channel; see `TradingStreamClient.subscribe`."""
    sent = dict(keys or {})
    manager = self.socket.subscribe(
      routing_key(channel, sent),
      {'keys': sent, 'private': private},
      request_channel=channel,
    )
    if validator is None or not (self.validate if validate is None else validate):
      return cast(StreamManager[T, Any, Any], manager)
    return manager.map(validator.python)
