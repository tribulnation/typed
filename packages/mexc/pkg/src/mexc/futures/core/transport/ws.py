"""Futures WebSocket transport: two independent connections behind one `StreamClient`.

Public subscriptions need no auth. Private subscriptions authenticate the *connection*
itself: a `login` frame, signed the same way as futures HTTP, unlocks all seven personal
channels on that connection -- there is no per-channel subscribe request and no listen
key, unlike spot. Both connections' replies carry no correlation id, so both compose
`typed_core.ws.SerialReplies`.
"""

from typing_extensions import Any, Mapping, TypedDict, TypeVar, cast
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import orjson

from typed_core.exceptions import AuthError
from typed_core.times import EpochConverter
from typed_core.util import StreamManager
from typed_core.validation import validator
from typed_core.ws import SerialReplies, Streams
from typed_core.ws.streams import Subscription

from ....core.auth import Credentials
from ....core.endpoint.stream import StreamClient
from ..auth import sign

T = TypeVar('T')

MEXC_FUTURES_SOCKET_URL = 'wss://contract.mexc.com/edge'

request_time = EpochConverter.milliseconds()


class Reply(TypedDict):
  """One non-push frame: a subscribe/unsubscribe/login/pong ack. Carries no correlation
  id, so replies are matched to requests by arrival order alone.
  """

  channel: str
  data: Any
  ts: datetime


validate_reply = validator(Reply)


@dataclass
class PublicConnection(SerialReplies[Reply], Streams[Any, Any, Reply, Reply]):
  """The public futures WS connection: no auth, plain-JSON `sub.<x>`/`push.<x>` frames."""

  url: str = MEXC_FUTURES_SOCKET_URL
  ping_interval: timedelta = field(default=timedelta(seconds=15), kw_only=True)

  async def send(self, msg: object):
    await (await self.ws).send(orjson.dumps(msg), text=True)

  async def send_request(self, method: str, params: Any = None) -> Reply:
    msg: dict = {'method': method}
    if params is not None:
      msg['param'] = params
    return await self.request(msg)

  async def ping(self, ws):
    await ws.send(orjson.dumps({'method': 'ping'}), text=True)

  async def request_subscription(self, channel: str, params: Any = None) -> Reply:
    return await self.send_request(f'sub.{channel}', params)

  async def request_unsubscription(self, channel: str, params: Any = None) -> Reply:
    return await self.send_request(f'unsub.{channel}')

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    reply = validate_reply.json(msg)
    if reply['channel'].startswith('push.'):
      channel = reply['channel'].removeprefix('push.')
      return {'channel': channel, 'notification': reply['data']}
    self.replies.put_nowait(reply)


@dataclass(kw_only=True)
class PrivateConnection(SerialReplies[Reply], Streams[Any, Any, None, None]):
  """The private futures WS connection: `login`-gated, all seven personal channels push
  by default once authenticated -- there is no per-channel subscribe request.
  """

  credentials: Credentials
  url: str = MEXC_FUTURES_SOCKET_URL
  ping_interval: timedelta = field(default=timedelta(seconds=15), kw_only=True)
  logged_in: asyncio.Event = field(default_factory=asyncio.Event, init=False, repr=False)
  login_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  async def send(self, msg: object):
    await (await self.ws).send(orjson.dumps(msg), text=True)

  async def send_request(self, method: str, params: Any = None) -> Reply:
    msg: dict = {'method': method}
    if params is not None:
      msg['param'] = params
    return await self.request(msg)

  async def ping(self, ws):
    await ws.send(orjson.dumps({'method': 'ping'}), text=True)

  async def login(self):
    if self.login_lock.locked() or self.logged_in.is_set():
      return
    async with self.login_lock:
      t = request_time.now()
      signature = sign(f'{self.credentials.api_key}{t}', secret=self.credentials.api_secret)
      reply = await self.send_request('login', {
        'apiKey': self.credentials.api_key, 'reqTime': t, 'signature': signature,
      })
      if reply['data'] != 'success':
        raise AuthError(f'Failed to log in to futures private WebSocket: {reply}')
      self.logged_in.set()

  async def request_subscription(self, channel: str, params: Any = None) -> None:
    await self.login()

  async def request_unsubscription(self, channel: str, params: Any = None) -> None:
    await self.login()

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    reply = validate_reply.json(msg)
    if reply['channel'].startswith('push.'):
      channel = reply['channel'].removeprefix('push.')
      return {'channel': channel, 'notification': reply['data']}
    self.replies.put_nowait(reply)


@dataclass(kw_only=True)
class SocketStreamClient(StreamClient):
  """Futures WS client: composes a public connection and a login-gated private one."""

  credentials: Credentials | None
  """`None` means unauthenticated: `authed_subscribe` raises `AuthError` on connect."""
  url: str = MEXC_FUTURES_SOCKET_URL
  public: PublicConnection = field(init=False)
  _private: PrivateConnection | None = field(default=None, init=False, repr=False)

  def __post_init__(self):
    self.public = PublicConnection(url=self.url)

  @classmethod
  def new(cls, url: str = MEXC_FUTURES_SOCKET_URL, *, credentials: Credentials | None = None):
    """Build one subtree. Thin: no environment lookup -- the root's `.new()` owns that."""
    return cls(url=url, credentials=credentials)

  async def __aenter__(self):
    await self.public.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.public.__aexit__(exc_type, exc_value, traceback)
    if self._private is not None:
      await self._private.__aexit__(exc_type, exc_value, traceback)

  def _private_connection(self) -> PrivateConnection:
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    if self._private is None:
      self._private = PrivateConnection(url=self.url, credentials=self.credentials)
    return self._private

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    manager = self.public.subscribe(channel, params)
    if validator is None:
      return cast('StreamManager[T, Any, Any]', manager)
    return manager.map(validator)

  def authed_subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    async def connect():
      conn = self._private_connection()
      await conn.__aenter__()
      stream = await conn.subscribe(channel, params)
      return stream if validator is None else stream.map(validator)
    return StreamManager(connect)
