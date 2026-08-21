from typing_extensions import Any, TypedDict
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio

from typed_core.validation import validator
from typed_mexc.core import timestamp_millis as ts
from typed_mexc.core.auth import resolve_credentials
from typed_mexc.spot.core import MEXC_SPOT_API_BASE, AuthHttpClient
from typed_mexc.spot.core.envelope import unwrap
from .client import StreamsClient, MEXC_SPOT_SOCKET_URL

class ListenResponse(TypedDict):
  """Single listen-key response payload."""
  listenKey: str

class ListenListResponse(TypedDict):
  """Valid listen-key list response payload."""
  listenKey: list[str]

listen_response = validator(ListenResponse)
list_response = validator(ListenListResponse)

def parse_listen_response(payload: Any) -> str:
  """Extract the `listenKey` field from an already-unwrapped single-key response."""
  return listen_response.python(payload)['listenKey']

def parse_listen_list_response(payload: Any) -> list[str]:
  """Extract the `listenKey` field from an already-unwrapped listen-key list response."""
  return list_response.python(payload)['listenKey']

@dataclass
class Context:
  ws: StreamsClient
  listen_key: str
  pinger: asyncio.Task

@dataclass
class UserStreamsClient:
  auth_http: AuthHttpClient
  api_url: str = MEXC_SPOT_API_BASE
  ws_url: str = MEXC_SPOT_SOCKET_URL
  keep_alive_every: timedelta = timedelta(minutes=30)
  ctx_future: asyncio.Future[Context] = field(default_factory=asyncio.Future, init=False)
  open_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  close_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

  class Config(TypedDict, total=False):
    keep_alive_every: timedelta

  @property
  async def ctx(self) -> Context:
    return await self.open()

  @classmethod
  def new(
    cls, api_key: str | None = None, api_secret: str | None = None, *,
    api_url: str = MEXC_SPOT_API_BASE,
    ws_url: str = MEXC_SPOT_SOCKET_URL,
    keep_alive_every: timedelta = timedelta(minutes=30),
  ):
    creds = resolve_credentials(api_key, api_secret)
    auth_http = AuthHttpClient(api_key=creds.api_key, api_secret=creds.api_secret)
    return cls(auth_http=auth_http, api_url=api_url, ws_url=ws_url, keep_alive_every=keep_alive_every)
  
  async def listen_key(self) -> str:
    """Open a new spot user-data-stream listen key."""
    r = await self.auth_http.signed_request('POST', self.api_url + '/api/v3/userDataStream', params={
      'timestamp': ts.now(),
    })
    return parse_listen_response(unwrap(r))

  async def list_keys(self) -> list[str]:
    """List the account's currently valid listen keys."""
    r = await self.auth_http.signed_request('GET', self.api_url + '/api/v3/userDataStream', params={
      'timestamp': ts.now(),
    })
    return parse_listen_list_response(unwrap(r))

  async def refresh_key(self, key: str) -> str:
    """Extend an existing listen key's validity."""
    r = await self.auth_http.signed_request('PUT', self.api_url + '/api/v3/userDataStream', params={
      'listenKey': key,
      'timestamp': ts.now(),
    })
    return parse_listen_response(unwrap(r))

  async def delete_key(self, key: str) -> str:
    """Close an existing listen key."""
    r = await self.auth_http.signed_request('DELETE', self.api_url + '/api/v3/userDataStream', params={
      'listenKey': key,
      'timestamp': ts.now(),
    })
    return parse_listen_response(unwrap(r))

  async def force_open(self):
    key = await self.listen_key()
    ws = await StreamsClient(url=self.ws_url + f'?listenKey={key}').__aenter__()
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
    await self.open()
    return self
  
  async def force_close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    ctx.pinger.cancel()
    await ctx.ws.__aexit__(exc_type, exc_value, traceback)
    await self.delete_key(ctx.listen_key)

  async def close(self, ctx: Context, exc_type=None, exc_value=None, traceback=None):
    if not self.close_lock.locked():
      async with self.close_lock:
        await self.force_close(ctx, exc_type, exc_value, traceback)

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.close(await self.ctx, exc_type, exc_value, traceback)

  async def pinger(self, key: str):
    while True:
      await asyncio.sleep(self.keep_alive_every.total_seconds())
      await self.refresh_key(key)

  async def subscribe(self, channel: str):
    ctx = await self.ctx
    return await ctx.ws.subscribe(channel)

@dataclass
class UserStreamsMixin:
  auth_ws: UserStreamsClient

  @classmethod
  def new(cls, api_key: str | None = None, api_secret: str | None = None, *,
    api_url: str = MEXC_SPOT_API_BASE,
    ws_url: str = MEXC_SPOT_SOCKET_URL,
  ):
    auth_ws = UserStreamsClient.new(api_key=api_key, api_secret=api_secret, api_url=api_url, ws_url=ws_url)
    return cls(auth_ws=auth_ws)

  async def __aenter__(self):
    await self.auth_ws.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.auth_ws.__aexit__(exc_type, exc_value, traceback)

  async def authed_subscribe(self, channel: str):
    return await self.auth_ws.subscribe(channel)
