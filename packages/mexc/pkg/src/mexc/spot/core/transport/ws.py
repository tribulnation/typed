"""Spot WebSocket transport: two independent connections behind one `StreamClient`.

Public subscriptions need no auth and dial `MEXC_SPOT_SOCKET_URL` directly. Private
subscriptions authenticate the *connection*, not each message: a listen key is minted
over signed spot HTTP, appended to the URL as `?listenKey=<key>`, refreshed on a timer,
and released on close -- so the private connection is a second, separately-managed
socket rather than a flag on the public one. Both connections' subscribe/unsubscribe
acks carry no correlation id (`{"id": 0, ...}` always), so both compose
`typed_core.ws.SerialReplies` rather than tracking message ids.
"""

from typing_extensions import Any, Mapping, TypedDict, TypeVar, cast
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import orjson

from typed_core.exceptions import ValidationError
from typed_core.util import Stream, StreamManager
from typed_core.validation import validator
from typed_core.ws import SerialReplies, Streams
from typed_core.ws.streams import Subscription

from ...streams.core.proto import PushDataV3ApiWrapper
from ....core.auth import Credentials
from ....core.endpoint.stream import StreamClient
from .http import HttpRpcClient, MEXC_SPOT_API_BASE

T = TypeVar('T')

MEXC_SPOT_SOCKET_URL = 'wss://wbs-api.mexc.com/ws'


class Reply(TypedDict):
  """Acknowledges a subscribe/unsubscribe/ping request. Carries no correlation id --
  `id` is always `0` -- so replies are matched to requests by arrival order alone.
  """

  id: int
  code: int
  msg: str


validate_reply = validator(Reply)


@dataclass
class Connection(SerialReplies[Reply], Streams[PushDataV3ApiWrapper, Any, Reply, Reply]):
  """One physical spot WS connection: JSON subscribe/unsubscribe envelope, protobuf pushes."""

  url: str = MEXC_SPOT_SOCKET_URL
  ping_interval: timedelta = field(default=timedelta(seconds=15), kw_only=True)

  async def send(self, msg: object):
    await (await self.ws).send(orjson.dumps(msg), text=True)

  async def ping(self, ws):
    await ws.send(orjson.dumps({'method': 'PING'}), text=True)

  async def request_subscription(self, channel: str, params=None) -> Reply:
    return await self.request({'method': 'SUBSCRIPTION', 'params': [channel]})

  async def request_unsubscription(self, channel: str, params=None) -> Reply:
    return await self.request({'method': 'UNSUBSCRIPTION', 'params': [channel]})

  def parse_msg(self, msg: str | bytes) -> Subscription[PushDataV3ApiWrapper] | None:
    try:
      reply = validate_reply.json(msg)
      self.replies.put_nowait(reply)
    except ValidationError:
      proto = PushDataV3ApiWrapper.parse(msg)  # type: ignore
      return {'channel': proto.channel, 'notification': proto}


class ListenKey(TypedDict):
  listenKey: str


validate_listen_key = validator(ListenKey)


@dataclass
class PrivateConnection:
  """A private socket bound to one listen key, plus the task that keeps it alive."""

  socket: Connection
  listen_key: str
  refresher: asyncio.Task


@dataclass(kw_only=True)
class SocketStreamClient(StreamClient):
  """Spot WS client: composes a public connection and a lazily-opened private one."""

  http: HttpRpcClient
  """Signed spot HTTP transport, reused to mint/refresh/release listen keys."""
  url: str = MEXC_SPOT_SOCKET_URL
  keep_alive_every: timedelta = timedelta(minutes=30)
  public: Connection = field(init=False)
  _private: 'asyncio.Future[PrivateConnection] | None' = field(default=None, init=False, repr=False)
  _open_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  def __post_init__(self):
    self.public = Connection(url=self.url)

  @classmethod
  def new(
    cls,
    url: str = MEXC_SPOT_SOCKET_URL,
    *,
    credentials: Credentials | None = None,
    api_url: str = MEXC_SPOT_API_BASE,
    validate: bool = True,
    keep_alive_every: timedelta = timedelta(minutes=30),
  ):
    """Build one subtree. Thin: no environment lookup -- the root's `.new()` owns that."""
    http = HttpRpcClient(base_url=api_url, credentials=credentials, validate=validate)
    return cls(http=http, url=url, keep_alive_every=keep_alive_every)

  async def __aenter__(self):
    await self.public.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.public.__aexit__(exc_type, exc_value, traceback)
    if self._private is not None and self._private.done():
      conn = self._private.result()
      conn.refresher.cancel()
      await conn.socket.__aexit__(exc_type, exc_value, traceback)
      await self.http.authed_request('DELETE', '/api/v3/userDataStream', params={'listenKey': conn.listen_key})
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def _refresher(self, listen_key: str):
    while True:
      await asyncio.sleep(self.keep_alive_every.total_seconds())
      await self.http.authed_request('PUT', '/api/v3/userDataStream', params={'listenKey': listen_key}, validator=validate_listen_key)

  async def _open_private(self) -> PrivateConnection:
    if self._open_lock.locked() or (self._private is not None and self._private.done()):
      return await cast('asyncio.Future[PrivateConnection]', self._private)

    async with self._open_lock:
      self._private = asyncio.Future()
      key = (await self.http.authed_request('POST', '/api/v3/userDataStream', validator=validate_listen_key))['listenKey']
      socket = Connection(url=f'{self.url}?listenKey={key}')
      await socket.__aenter__()
      conn = PrivateConnection(socket=socket, listen_key=key, refresher=asyncio.create_task(self._refresher(key)))
      self._private.set_result(conn)
      return conn

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    manager = self.public.subscribe(channel)
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
      conn = await self._open_private()
      stream = await conn.socket.subscribe(channel)
      if validator is None:
        return cast('Stream[T, Any, Any]', stream)
      return stream.map(validator)
    return StreamManager(connect)
