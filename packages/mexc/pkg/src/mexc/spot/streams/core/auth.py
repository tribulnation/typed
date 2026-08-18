from typing_extensions import TypedDict
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import os
import pydantic

from mexc.core import timestamp as ts, ApiError
from mexc.spot.core import MEXC_SPOT_API_BASE, AuthHttpClient
from .client import StreamsClient, MEXC_SPOT_SOCKET_URL

class ListenResponse(TypedDict):
  listenKey: str

class ListenListResponse(TypedDict):
  listenKey: list[str]

class ErrorResponse(TypedDict):
  code: int
  msg: str

Response = ListenResponse | ErrorResponse
ListResponse = ListenListResponse | ErrorResponse

response_adapter = pydantic.TypeAdapter(Response)
list_response_adapter = pydantic.TypeAdapter(ListResponse)

def validate_listen_response(content: str) -> str:
  obj = response_adapter.validate_json(content)
  if 'listenKey' in obj:
    return obj['listenKey']
  else:
    raise ApiError(obj)

def validate_listen_list_response(content: str) -> list[str]:
  obj = list_response_adapter.validate_json(content)
  if 'listenKey' in obj:
    return obj['listenKey']
  else:
    raise ApiError(obj)

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
    if api_key is None:
      api_key = os.environ['MEXC_ACCESS_KEY']
    if api_secret is None:
      api_secret = os.environ['MEXC_SECRET_KEY']
    auth_http = AuthHttpClient(api_key=api_key, api_secret=api_secret)
    return cls(auth_http=auth_http, api_url=api_url, ws_url=ws_url, keep_alive_every=keep_alive_every)
  
  async def listen_key(self):
    r = await self.auth_http.signed_request('POST', self.api_url + '/api/v3/userDataStream', params={
      'timestamp': ts.now(),
    })
    return validate_listen_response(r.text)

  async def list_keys(self) -> list[str]:
    r = await self.auth_http.signed_request('GET', self.api_url + '/api/v3/userDataStream', params={
      'timestamp': ts.now(),
    })
    return validate_listen_list_response(r.text)
  
  async def refresh_key(self, key: str):
    r = await self.auth_http.signed_request('PUT', self.api_url + '/api/v3/userDataStream', params={
      'listenKey': key,
      'timestamp': ts.now(),
    })
    return validate_listen_response(r.text)
  
  async def delete_key(self, key: str):
    r = await self.auth_http.signed_request('DELETE', self.api_url + '/api/v3/userDataStream', params={
      'listenKey': key,
      'timestamp': ts.now(),
    })
    return validate_listen_response(r.text)

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
