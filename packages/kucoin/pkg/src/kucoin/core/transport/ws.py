"""WebSocket transport: the bullet-token handshake, and subscribe/unsubscribe over a
dynamically-resolved connection.

Two instances share this one implementation — Spot/Margin and Futures — differing only
in which host's bullet endpoint (`POST /api/v1/bullet-public`/`bullet-private`) resolves
the actual connection. See `spec/core.md` §WebSocket for the frame shapes and why no
`typed_core.ws.SerialReplies` is used despite acks carrying a correlation id.
"""

from typing_extensions import Any, Literal, NotRequired, Self, TypeVar, cast
from dataclasses import dataclass, field
from datetime import timedelta
import json as _json
import asyncio

from typed_core.exceptions import AuthError, BadRequest
from typed_core.validation import TypedDict, validator
from typed_core.util import StreamManager
from typed_core.ws.streams import Streams, Subscription

from ..endpoint.stream import StreamClient
from ..auth import Credentials
from .http import HttpRpcClient

T = TypeVar('T')


class InstanceServer(TypedDict):
  """One candidate WebSocket host, as returned by a bullet-token call."""

  endpoint: str
  """WebSocket URL to dial — dynamic; never hardcode a `wss://` host instead."""
  encrypt: bool
  protocol: Literal['websocket']
  pingInterval: int
  """Recommended ping interval, in milliseconds."""
  pingTimeout: int
  """Heartbeat timeout, in milliseconds."""


class BulletToken(TypedDict):
  """Response of `POST /api/v1/bullet-public` or `/api/v1/bullet-private`."""

  token: str
  instanceServers: list[InstanceServer]


validate_bullet_token = validator(BulletToken)


async def fetch_bullet_token(bullet: HttpRpcClient, *, private: bool) -> BulletToken:
  """Call the bullet-token endpoint and return its payload.

  Args:
    bullet: `HttpRpcClient` rooted at the REST base URL of the instance being connected
      to (`api.kucoin.com` for Spot/Margin, `api-futures.kucoin.com` for Futures).
    private: Use `bullet-private` (signed, required for private topics) instead of
      `bullet-public`.
  """
  path = '/api/v1/bullet-private' if private else '/api/v1/bullet-public'
  if private:
    return await bullet.authed_request('POST', path, validator=validate_bullet_token)
  return await bullet.request('POST', path, validator=validate_bullet_token)


class Frame(TypedDict):
  """Any frame KuCoin sends: a topic push, a subscribe/unsubscribe ack, an error, the
  post-connect welcome, or a pong. Every field but `type` is optional because the shape
  varies by kind — `Push`/`Reply` re-validate the stricter shape once a frame is routed.
  """

  id: NotRequired[str]
  type: Literal['message', 'ack', 'error', 'welcome', 'pong']
  topic: NotRequired[str]
  subject: NotRequired[str]
  data: NotRequired[Any]
  code: NotRequired[int]


validate_frame = validator(Frame)


class Push(TypedDict):
  """One topic push."""

  type: Literal['message']
  topic: str
  subject: str
  data: Any


validate_push = validator(Push)


class Reply(TypedDict):
  """Acknowledges — or rejects — a subscribe/unsubscribe."""

  id: NotRequired[str]
  type: Literal['ack', 'error']
  code: NotRequired[int]
  """Present only when `type` is `'error'`."""
  data: NotRequired[Any]
  """Present only when `type` is `'error'`."""


validate_reply = validator(Reply)


def _dumps(msg: Any) -> str:
  return _json.dumps(msg, separators=(',', ':'))


@dataclass
class SocketConnection(Streams[Push, bool, Reply, Reply]):
  """One Spot/Margin or Futures instance connection.

  One physical connection serves both public and private topics once it's opened with a
  private bullet token — KuCoin does not split them across separate sockets the way it
  splits Spot/Margin from Futures. `private` therefore gates the *connection* (which
  bullet endpoint authenticates it, and so which topics it's even allowed to subscribe
  to), while each individual subscribe's `privateChannel` frame field is the `params`
  argument to `request_subscription`/`request_unsubscription` — a public and a private
  topic can coexist on the one socket, each stating its own. `SocketStreamClient` below
  is what actually picks that value, via `subscribe` vs `authed_subscribe`.

  `url` starts empty and is resolved fresh on every `force_open` — bullet tokens are
  single-use-connection scoped, so a reconnect needs a new one regardless of whether the
  previous host is still reachable.
  """

  bullet: HttpRpcClient = field(kw_only=True)
  """`HttpRpcClient` rooted at this instance's REST base URL, reused only for the bullet
  call."""
  private: bool = field(default=False, kw_only=True)
  """Request a private bullet token, granting this connection access to private topics."""
  url: str = field(default='', kw_only=True)
  counter: int = field(default=0, init=False, repr=False)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: 'asyncio.Queue[Reply]' = field(
    default_factory=asyncio.Queue, init=False, repr=False
  )

  def next_id(self) -> str:
    self.counter += 1
    return str(self.counter)

  async def send(self, msg: Any):
    await (await self.ws).send(_dumps(msg))

  async def command(self, msg: Any) -> Reply:
    """Send one subscribe/unsubscribe frame and wait for its ack, serialized against
    every other concurrent command — "the next reply" is unambiguous this way without
    needing to match on `id`, the same choice bybit made for a venue whose acks carry no
    id at all.
    """
    async with self.lock:
      await self.send(msg)
      reply = await self.wait(self.replies.get())
    if reply['type'] == 'error':
      raise BadRequest(reply)
    return reply

  async def force_open(self):
    """Fetch a fresh bullet token, then connect to whichever host it names.

    Sets `url`/`ping_interval`/`timeout` from the token response before delegating to
    `typed_core.ws.Socket.force_open` — the response is authoritative, never a hardcoded
    `wss://` host (`spec/discovery.md` §Domains).
    """
    token = await fetch_bullet_token(self.bullet, private=self.private)
    server = token['instanceServers'][0]
    connect_id = self.next_id()
    self.url = f'{server["endpoint"]}?token={token["token"]}&connectId={connect_id}'
    self.ping_interval = timedelta(milliseconds=server['pingInterval'])
    self.timeout = timedelta(milliseconds=server['pingTimeout'])
    return await super().force_open()

  async def ping(self, ws):
    await ws.send(_dumps({'id': self.next_id(), 'type': 'ping'}))

  def parse_msg(self, msg: str | bytes) -> Subscription[Push] | None:
    frame = validate_frame(msg)
    if 'topic' not in frame:
      if frame['type'] in ('ack', 'error'):
        self.replies.put_nowait(validate_reply(frame))
      return None  # welcome/pong: nothing to route
    return Subscription(channel=frame['topic'], notification=validate_push(frame))

  async def request_subscription(
    self, channel: str, params: bool | None = None
  ) -> Reply:
    """`channel` is the full topic string, e.g. `/market/ticker:BTC-USDT`. `params` is
    this topic's own `privateChannel` value."""
    return await self.command(
      {
        'id': self.next_id(),
        'type': 'subscribe',
        'topic': channel,
        'privateChannel': params or False,
        'response': True,
      }
    )

  async def request_unsubscription(
    self, channel: str, params: bool | None = None
  ) -> Reply:
    return await self.command(
      {
        'id': self.next_id(),
        'type': 'unsubscribe',
        'topic': channel,
        'privateChannel': params or False,
        'response': True,
      }
    )


def _data(push: Push) -> Any:
  return push['data']


@dataclass(kw_only=True)
class SocketStreamClient(StreamClient):
  """WebSocket streams client for one KuCoin instance (Spot/Margin or Futures), owning
  connection, authentication and validation.
  """

  conn: SocketConnection
  credentials: Credentials | None
  """Mirrors `conn.bullet.credentials` — `None` means this connection was opened with a
  public bullet token, so `authed_subscribe` has nothing to authenticate a private topic
  with, and fails fast rather than round-tripping to KuCoin for a rejection."""
  validate: bool = True

  @classmethod
  def new(
    cls,
    *,
    bullet: HttpRpcClient,
    private: bool,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
  ) -> Self:
    """Build one connection against an already-resolved bullet `HttpRpcClient`.

    Thin: no environment lookup, no region resolution — the root's `.new()` owns that,
    see `kucoin.main.KuCoin.new`. `ping_interval` is left at `Socket`'s default; the real
    value is server-declared and set fresh on every `SocketConnection.force_open`, not
    something a static parameter here could know ahead of connecting.
    """
    conn = SocketConnection(url='', bullet=bullet, private=private, timeout=timeout)
    return cls(conn=conn, credentials=bullet.credentials, validate=validate)

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    await self.conn.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.conn.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    manager = self.conn.subscribe(channel, params=False)
    if validator is not None and self.should_validate(validate):
      return manager.map(lambda push: validator(push['data']))
    return cast(StreamManager[T, Any, Any], manager.map(_data))

  def authed_subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Raises:
    AuthError: `credentials` is `None` — this connection was opened with a public
      bullet token, so it was never granted access to private topics.
    """
    if self.credentials is None:
      raise AuthError(
        f'{channel} requires credentials; build the client with '
        '`KuCoin.new(api_key=..., api_secret=..., api_passphrase=...)`.'
      )
    manager = self.conn.subscribe(channel, params=True)
    if validator is not None and self.should_validate(validate):
      return manager.map(lambda push: validator(push['data']))
    return cast(StreamManager[T, Any, Any], manager.map(_data))
