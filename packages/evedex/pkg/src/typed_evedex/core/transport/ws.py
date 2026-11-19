"""WebSocket transport: the Centrifugo v5 JSON protocol.

One connection carries every subscription. Commands are `{"id": N, "<command>": {...}}`
and their replies echo `id`; publications arrive as `{"push": {"channel", "pub": {"data"}}}`.
One frame may hold several newline-separated messages. The server pings with `{}` and the
client must answer `{}`. A `connect` command opens the session; it carries no token, since
public channels need none and private ones authorize per subscription with
`data: {accessToken}` (checked by the Auth service's subscribe proxy).

The server can end a subscription on its own, with an `unsub` push naming the channel, or
the whole session, with a `disconnect` push. Either is queued to every stream it ends as an
`Ended` marker in place of a publication, which the stream raises when it reaches it:
`NetworkError` when the Centrifugo code says to resubscribe (or reconnect), `ApiError`
when it says not to. The server closes the socket right after a `disconnect`, and work
bound to a closed connection raises `Context.failure()`: a plain `NetworkError`, racing
the queued markers. So the connection's `CentrifugoContext` records the push, its
`failure()` is the classified error from then on, and a stream that fails with a plain
`NetworkError` first lets the listener drain what the server sent before the close, then
raises the classified error if a `disconnect` was among it.
"""

from typing_extensions import (
  Any,
  AsyncIterable,
  Callable,
  Literal,
  Mapping,
  NotRequired,
  TypedDict,
  TypeVar,
  cast,
)
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from datetime import timedelta
import asyncio
import json
import logging

import websockets

from typed_core.util import Stream, StreamManager
from typed_core.validation import validator
from typed_core.ws import StreamsRpc
from typed_core.ws.socket import Context
from typed_core.ws.streams_rpc import Message

from ..auth import Session
from ..endpoint.stream import Namespace, StreamClient
from ..exc import ApiError, AuthError, BadRequest, NetworkError
from ..wire import loads

T = TypeVar('T')

logger = logging.getLogger(__name__)

MARKET_DATA_NAMESPACE = 'market-data'

RESUBSCRIBE_FROM = 2500
"""`unsub` push codes from this one up make Centrifugo clients resubscribe; lower codes
are final (centrifugal.dev/docs/server/codes)."""
RECONNECT_CODES = range(3000, 3500)
"""`disconnect` push codes after which Centrifugo clients reconnect; higher codes are final."""

UNKNOWN_CHANNEL = 102
PERMISSION_DENIED = 103
BAD_REQUEST = 107
TOKEN_EXPIRED = 109
"""Centrifugo client-protocol error codes that map onto a specific exception."""

LISTENING: ContextVar[websockets.ClientConnection | None] = ContextVar(
  'typed_evedex.ws.listening', default=None
)
"""The connection whose listener task is running the current `on_msg`, set by that task."""


class CommandError(TypedDict):
  """A Centrifugo command error."""

  code: int
  message: str


class Reply(TypedDict, total=False):
  """A reply to one command: exactly one of the command's own key, or `error`."""

  connect: Mapping[str, Any]
  subscribe: Mapping[str, Any]
  unsubscribe: Mapping[str, Any]
  error: CommandError


class SubscriptionParams(TypedDict):
  """What `request_subscription` needs beyond the channel name."""

  private: bool


Command = Mapping[Literal['connect', 'subscribe', 'unsubscribe'], Mapping[str, Any]]


def raise_error(error: CommandError, *, channel: str | None = None):
  """Raise the `typed_core` exception matching a Centrifugo command error.

  Raises:
    AuthError: Permission denied or expired token.
    BadRequest: Unknown channel or malformed command.
    ApiError: Any other code.
  """
  code = error['code']
  context = {'channel': channel, **error} if channel else dict(error)
  if code in (PERMISSION_DENIED, TOKEN_EXPIRED):
    raise AuthError(context)
  if code in (UNKNOWN_CHANNEL, BAD_REQUEST):
    raise BadRequest(context)
  raise ApiError(context)


class Closure(TypedDict):
  """Why the server ended a subscription (`unsub`) or the session (`disconnect`)."""

  code: int
  reason: NotRequired[str]


class Push(TypedDict):
  """The `push` of a server message: `pub` for a publication, `unsub` when the server
  ends the subscription to `channel`, `disconnect` when it ends the whole session."""

  channel: NotRequired[str]
  pub: NotRequired[Mapping[str, Any]]
  unsub: NotRequired[Closure]
  disconnect: NotRequired[Closure]


@dataclass(frozen=True)
class Ended:
  """Queued to a stream in place of a publication once the server has ended it."""

  error: NetworkError | ApiError
  """What the stream raises when it reaches this marker."""


def unsubscribed_error(channel: str, closure: Closure) -> NetworkError | ApiError:
  """The error for a server-side `unsub` of `channel`: `NetworkError` if Centrifugo says
  to resubscribe, else `ApiError`."""
  context = {'channel': channel, 'unsub': dict(closure)}
  if closure['code'] >= RESUBSCRIBE_FROM:
    return NetworkError(context)
  return ApiError(context)


def disconnected_error(closure: Closure) -> NetworkError | ApiError:
  """The error for a server-side `disconnect`: `NetworkError` if Centrifugo says to
  reconnect, else `ApiError`."""
  context = {'disconnect': dict(closure)}
  if closure['code'] in RECONNECT_CODES:
    return NetworkError(context)
  return ApiError(context)


@dataclass
class CentrifugoContext(Context):
  """A connection that remembers the server's `disconnect` push, if it got one."""

  disconnect: Closure | None = None
  """The `disconnect` push received on this connection."""

  def failure(self) -> BaseException:
    """The classified `disconnect` error once the server has pushed one, whichever way
    the connection then went down; else `typed_core`'s own."""
    if self.disconnect is not None:
      return disconnected_error(self.disconnect)
    return super().failure()


def raise_ended(message: Any) -> Any:
  """Pass a publication through; raise the error of an `Ended` marker."""
  if isinstance(message, Ended):
    raise message.error
  return message


@dataclass
class CentrifugoConnection(
  StreamsRpc[Command, Reply, Any, SubscriptionParams, Reply, Reply]
):
  """One Centrifugo connection: connect handshake, ping replies, subscriptions."""

  session: Session | None = field(default=None, kw_only=True, repr=False)
  """The wallet's JWT session, for private subscriptions."""
  pending: set[asyncio.Task] = field(default_factory=set, init=False, repr=False)
  """Pong sends in flight, kept referenced until done and cancelled with the connection."""
  contexts: dict[websockets.ClientConnection, CentrifugoContext] = field(
    default_factory=dict, init=False, repr=False
  )
  """Each open connection's context, for its listener to record a `disconnect` on."""
  ended: set[str] = field(default_factory=set, init=False, repr=False)
  """Channels the server has unsubscribed, so closing their stream sends no `unsubscribe`."""

  def end(self, channel: str, error: NetworkError | ApiError):
    """End the stream of `channel`, if one is open: queue `error` to it."""
    queue = self.subscriptions.get(channel)
    if queue is None:
      return
    self.ended.add(channel)
    queue.put_nowait(Ended(error))

  def connection_closed(self, ctx: Context):
    """Forget the closed connection's server-ended channels and cancel its pongs. After a
    `disconnect` push, its pending replies fail with the push's classified error."""
    self.ended.clear()
    for task in self.pending:
      task.cancel()
    self.contexts.pop(ctx.ws, None)
    if isinstance(ctx, CentrifugoContext) and ctx.disconnect is not None:
      for reply in self.replies.values():
        if not reply.done():
          reply.set_exception(disconnected_error(ctx.disconnect))
          reply.exception()
    super().connection_closed(ctx)

  async def listener(self, ws: websockets.ClientConnection):
    """Listen on `ws`, marking it as the connection `on_msg` runs for."""
    LISTENING.set(ws)
    await super().listener(ws)

  async def force_open(self) -> Context:
    """Connect, then send Centrifugo's `connect` command and wait for its reply."""
    base = await super().force_open()
    # Registered before the first await, so before the listener reads anything.
    ctx = CentrifugoContext(ws=base.ws, listener=base.listener, pinger=base.pinger)
    self.contexts[ctx.ws] = ctx
    id = self.counter
    self.counter += 1
    self.replies[id] = reply = asyncio.Future[Reply]()
    try:
      await ctx.ws.send(json.dumps({'id': id + 1, 'connect': {}}))
      result = await self.wait(reply, ctx=ctx)
    except BaseException:
      await self.close(ctx)
      raise
    finally:
      self.replies.pop(id, None)
    if 'error' in result:
      await self.close(ctx)
      raise_error(result['error'])
    return ctx

  async def rpc_send(self, id: int, req: Command, /):
    """Send one command. Centrifugo reserves `id: 0` for no-reply, so ids start at 1."""
    ws = await self.ws
    await ws.send(json.dumps({'id': id + 1, **req}))

  async def pong(self, ws: websockets.ClientConnection):
    """Answer a server ping on the connection it arrived on."""
    try:
      await ws.send('{}')
    except Exception as e:
      logger.debug('Failed to answer a ping: %s', e)

  def on_msg(self, msg: str | bytes):
    """Split a frame into its messages; answer pings, route the rest."""
    text = msg.decode() if isinstance(msg, bytes) else msg
    for line in text.split('\n'):
      line = line.strip()
      if not line:
        continue
      if line == '{}':
        ws = LISTENING.get()
        if ws is None:
          logger.debug('Ignored a ping outside a listener')
          continue
        task = asyncio.ensure_future(self.pong(ws))
        self.pending.add(task)
        task.add_done_callback(self.pending.discard)
        continue
      super().on_msg(line)

  def parse_msg(self, msg: str | bytes, /) -> Message[Reply, Any] | None:
    """Read one message as a command reply or a channel publication."""
    obj = loads(msg)
    if not isinstance(obj, dict):
      return None
    if 'id' in obj:
      return {
        'kind': 'response',
        'id': int(obj['id']) - 1,
        'response': cast(Reply, obj),
      }
    push: Push | None = obj.get('push')
    if push is None:
      return None
    if 'pub' in push and 'channel' in push:
      return {
        'kind': 'subscription',
        'channel': push['channel'],
        'notification': push['pub'].get('data'),
      }
    if 'unsub' in push and 'channel' in push:
      channel = push['channel']
      logger.warning('Centrifugo unsubscribed %s: %s', channel, push['unsub'])
      self.end(channel, unsubscribed_error(channel, push['unsub']))
      return None
    if 'disconnect' in push:
      logger.warning('Centrifugo disconnected: %s', push['disconnect'])
      ws = LISTENING.get()
      if ws is not None and (ctx := self.contexts.get(ws)) is not None:
        ctx.disconnect = push['disconnect']
      error = disconnected_error(push['disconnect'])
      for channel in list(self.subscriptions):
        self.end(channel, error)
      return None
    logger.debug('Ignored Centrifugo push: %s', obj)
    return None

  async def request_subscription(
    self, channel: str, params: SubscriptionParams | None = None
  ) -> Reply:
    """Subscribe; a private channel sends the session's access token as `data`."""
    self.ended.discard(channel)
    command: dict[str, Any] = {'channel': channel}
    if params is not None and params['private']:
      if self.session is None:
        raise AuthError('Private channels need the wallet private key (a JWT session).')
      command['data'] = {'accessToken': await self.session.access_token()}
    reply = await self.rpc_request({'subscribe': command})
    if 'error' in reply:
      raise_error(reply['error'], channel=channel)
    return reply

  async def classified(
    self, ctx: Context, error: NetworkError
  ) -> NetworkError | ApiError:
    """The error to raise for `error` on `ctx`: the classified `disconnect` error if the
    server pushed one before closing, else `error` itself.

    The socket can read as closed while the listener still holds frames the server sent
    before the close, the `disconnect` push among them; the listener always reads those
    before it fails, so it is awaited (up to `timeout`) first.
    """
    if not isinstance(ctx, CentrifugoContext):
      return error
    if not ctx.listener.done():
      await asyncio.wait([ctx.listener], timeout=self.timeout.total_seconds())
    if ctx.disconnect is not None:
      return disconnected_error(ctx.disconnect)
    return error

  def subscribe(
    self,
    channel: str,
    params: SubscriptionParams | None = None,
    *,
    request_channel: str | None = None,
    message_key: Callable[[Any], str] | None = None,
    keep_latest: bool = False,
  ) -> StreamManager[Any, Reply, Reply]:
    """`StreamsRpc.subscribe`, raising the classified error of a `disconnect` the server
    pushed before closing (see `classified`), from the subscribe or the stream."""
    base = super().subscribe(
      channel,
      params,
      request_channel=request_channel,
      message_key=message_key,
      keep_latest=keep_latest,
    )

    async def iterate(ctx: Context, source: AsyncIterable[Any]) -> AsyncIterable[Any]:
      """Forward `source`, classifying its connection failure."""
      try:
        async for message in source:
          yield message
      except NetworkError as e:
        error = await self.classified(ctx, e)
        if error is e:
          raise
        raise error from e

    async def connect() -> Stream[Any, Reply, Reply]:
      """Subscribe on the current connection, classifying its failure."""
      ctx = await self.ctx
      try:
        stream = await base.connect()
      except NetworkError as e:
        error = await self.classified(ctx, e)
        if error is e:
          raise
        raise error from e
      return replace(stream, stream=iterate(ctx, stream.stream))

    return StreamManager(connect)

  async def request_unsubscription(
    self, channel: str, params: SubscriptionParams | None = None
  ) -> Reply:
    """Unsubscribe from `channel`; nothing is sent if the server already unsubscribed it."""
    if channel in self.ended:
      self.ended.discard(channel)
      return {}
    reply = await self.rpc_request({'unsubscribe': {'channel': channel}})
    if 'error' in reply:
      raise_error(reply['error'], channel=channel)
    return reply


@dataclass(kw_only=True)
class SocketStreamClient(StreamClient):
  """`StreamClient` over one Centrifugo connection, owning naming and validation."""

  conn: CentrifugoConnection
  prefix: str
  """The environment's exchange channel namespace."""
  validate: bool = True

  @classmethod
  def new(
    cls,
    url: str,
    *,
    prefix: str,
    session: Session | None = None,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
  ):
    """Build the stream client. The server drives keep-alive (`ping: 25`), so the client
    never pings on its own."""
    conn = CentrifugoConnection(url, timeout=timeout, session=session, max_size=None)
    return cls(conn=conn, prefix=prefix, validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def __aenter__(self):
    """Take ownership of the connection; it opens lazily on the first subscription."""
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection, if one was opened."""
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  def channel_name(self, channel: str, namespace: Namespace) -> str:
    """The full channel name, namespace prefix included."""
    prefix = self.prefix if namespace == 'exchange' else MARKET_DATA_NAMESPACE
    return f'{prefix}:{channel}'

  def validated(
    self,
    manager: StreamManager[Any, Any, Any],
    validator: validator[T] | None,
    validate: bool | None,
  ) -> StreamManager[T, Any, Any]:
    """Raise a server-ended stream's error, and map publications through `validator`
    unless validation is off."""
    checked = manager.map(raise_ended)
    if validator is None or not self.should_validate(validate):
      return cast(StreamManager[T, Any, Any], checked)
    return checked.map(validator.python)

  def subscribe(
    self,
    channel: str,
    *,
    namespace: Namespace = 'exchange',
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to a public channel."""
    manager = self.conn.subscribe(
      self.channel_name(channel, namespace), {'private': False}
    )
    return self.validated(manager, validator, validate)

  def authed_subscribe(
    self,
    channel: str,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to a private channel: `channel` suffixed with `-<exchangeId>`."""

    async def connect():
      """Resolve the account id, then subscribe with the session token."""
      session = self.conn.session
      if session is None:
        raise AuthError('Private channels need the wallet private key (a JWT session).')
      exchange_id = await session.user_exchange_id()
      name = self.channel_name(f'{channel}-{exchange_id}', 'exchange')
      return await self.conn.subscribe(name, {'private': True}).connect()

    return self.validated(StreamManager(connect), validator, validate)
