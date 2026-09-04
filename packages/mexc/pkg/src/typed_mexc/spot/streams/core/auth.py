"""Spot's private, listen-key-authenticated WebSocket connection: obtains and
maintains MEXC's listen key over REST (delegated to the same signed `SpotHttpClient`
every Spot HTTP call uses), then opens the same `SpotPublicStreamsClient` connection
with `?listenKey=...` appended -- MEXC's private feed is the public endpoint plus that
one query parameter, not a separate wire dialect.
"""

from typing_extensions import Any, TypedDict
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio

from typed_core.exceptions import AuthError
from typed_core.util import StreamManager
from typed_core.validation import validator

from typed_mexc.spot.core.client import SpotHttpClient
from .client import SpotPublicStreamsClient, MEXC_SPOT_SOCKET_URL


class ListenKeyResponse(TypedDict):
  """Single listen-key response payload."""

  listenKey: str


validate_listen_key = validator(ListenKeyResponse)


async def create_listen_key(http: SpotHttpClient) -> str:
  """Open a new Spot user-data-stream listen key."""
  return (
    await http.authed_request('POST', '/api/v3/userDataStream', validator=validate_listen_key)
  )['listenKey']


async def refresh_listen_key(http: SpotHttpClient, key: str) -> str:
  """Extend an existing listen key's validity."""
  return (
    await http.authed_request(
      'PUT', '/api/v3/userDataStream', {'listenKey': key}, validator=validate_listen_key,
    )
  )['listenKey']


async def close_listen_key(http: SpotHttpClient, key: str) -> str:
  """Close an existing listen key."""
  return (
    await http.authed_request(
      'DELETE', '/api/v3/userDataStream', {'listenKey': key}, validator=validate_listen_key,
    )
  )['listenKey']


@dataclass
class Context:
  """One opened private connection: the live socket, its listen key, and the
  background task keeping that key alive."""

  ws: SpotPublicStreamsClient
  listen_key: str
  pinger: 'asyncio.Task[None]'


@dataclass
class SpotPrivateStreamsClient:
  """Lazily opens Spot's private WebSocket connection on first use, refreshing its
  listen key on a timer for as long as the connection stays open."""

  http: SpotHttpClient
  url: str = MEXC_SPOT_SOCKET_URL
  keep_alive_every: timedelta = timedelta(minutes=30)
  ctx_future: 'asyncio.Future[Context]' = field(default_factory=asyncio.Future, init=False)
  open_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  close_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

  @property
  async def ctx(self) -> Context:
    return await self.open()

  async def force_open(self) -> Context:
    if self.http.credentials is None:
      raise AuthError('MEXC API credentials are required for private Spot streams.')
    key = await create_listen_key(self.http)
    ws = await SpotPublicStreamsClient(url=f'{self.url}?listenKey={key}').__aenter__()
    pinger = asyncio.create_task(self.pinger(key))
    return Context(ws=ws, listen_key=key, pinger=pinger)

  async def open(self) -> Context:
    if self.open_lock.locked() or self.ctx_future.done():
      return await self.ctx_future
    async with self.open_lock:
      ctx = await self.force_open()
      self.ctx_future.set_result(ctx)
      return ctx

  async def __aenter__(self):
    """Deliberately does not open the connection (ADR 0003, ADR 0003's "lazy
    connections" assumption -- unlike `typed_core`'s own transport primitives, opening
    this one is real network I/O, minting a listen key that needs real credentials, so
    a `public=True` client's root `__aenter__` must not force it just by composing this
    client in. The first real `.subscribe()` call still opens it lazily via `.ctx`."""
    return self

  async def force_close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    ctx.pinger.cancel()
    await ctx.ws.__aexit__(exc_type, exc_value, traceback)
    await close_listen_key(self.http, ctx.listen_key)

  async def close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    if not self.close_lock.locked():
      async with self.close_lock:
        await self.force_close(ctx, exc_type, exc_value, traceback)

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Only closes a connection this client actually opened -- the mirror image of
    `__aenter__`'s own no-op: closing something never opened would force the exact
    open-then-close round trip `__aenter__` was just fixed to avoid."""
    if self.ctx_future.done():
      await self.close(await self.ctx, exc_type, exc_value, traceback)

  async def pinger(self, key: str):
    while True:
      await asyncio.sleep(self.keep_alive_every.total_seconds())
      await refresh_listen_key(self.http, key)

  def subscribe(self, channel: str, params: Any = None):
    """Subscribe over the (lazily-opened) private connection -- same shape as
    `SpotPublicStreamsClient.subscribe`, so `SpotStreamsEndpoint` can treat both
    uniformly."""

    async def connect():
      ctx = await self.ctx
      return await ctx.ws.subscribe(channel, params)

    return StreamManager(connect)
