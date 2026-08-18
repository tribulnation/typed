from typing_extensions import Any
from dataclasses import dataclass, field
import asyncio
import os
from datetime import timedelta
import orjson

from typed_core.ws.streams import Streams, Subscription
from mexc.core import timestamp as ts, AuthError, ValidationMixin
from mexc.futures.core import sign
from .client import validate_reply, Reply, MEXC_FUTURES_SOCKET_URL

@dataclass
class AuthedStreamsClient(Streams[Any, Any, None, None]):
  api_key: str
  api_secret: str
  auth_lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
  authorized: asyncio.Event = field(default_factory=asyncio.Event, init=False)
  ping_interval: timedelta = field(default=timedelta(seconds=15), kw_only=True)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: asyncio.Queue[Reply] = field(default_factory=asyncio.Queue, init=False)

  @classmethod
  def new(
    cls, api_key: str | None = None, api_secret: str | None = None, *,
    url: str = MEXC_FUTURES_SOCKET_URL,
  ):
    if api_key is None:
      api_key = os.environ['MEXC_ACCESS_KEY']
    if api_secret is None:
      api_secret = os.environ['MEXC_SECRET_KEY']
    return cls(api_key=api_key, api_secret=api_secret, url=url)

  async def send(self, msg):
    await (await self.ws).send(orjson.dumps(msg), text=True)

  async def send_request(self, method: str, params=None):
    msg = {'method': method}
    if params is not None:
      msg['param'] = params
    await self.send(msg)

  async def request(self, method: str, params=None):
    async with self.lock:
      await self.send_request(method, params)
      return await self.replies.get()

  async def ping(self, ws):
    await ws.send(orjson.dumps({'method': 'ping'}), text=True)

  @property
  async def authed(self):
    await self.authenticate()

  async def authenticate(self):
    if self.auth_lock.locked() or self.authorized.is_set():
      return

    async with self.auth_lock:
      await self.login()
      self.authorized.set()

  async def login(self):
    t = ts.now()
    signature = sign(f'{self.api_key}{t}', secret=self.api_secret)
    r: Reply = await self.request('login', {
        'apiKey': self.api_key,
        'reqTime': t,
        'signature': signature,
      })
    if r['data'] != 'success':
      raise AuthError(f'Failed to login: {r}')
    return r
  
  async def request_subscription(self, channel: str, params=None):
    await self.authed
  
  async def request_unsubscription(self, channel: str, params=None):
    await self.authed

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    r = validate_reply(msg)
    if r['channel'].startswith('push.'):
      channel = r['channel'].removeprefix('push.')
      return {'channel': channel, 'notification': r['data']}
    else:
      self.replies.put_nowait(r)

@dataclass
class AuthedStreamsMixin(ValidationMixin):
  auth_ws: AuthedStreamsClient | None

  @property
  def authenticated_ws(self) -> AuthedStreamsClient:
    if self.auth_ws is None:
      raise AuthError('MEXC API credentials are required for authenticated futures streams.')
    return self.auth_ws

  @classmethod
  def new(cls, api_key: str | None = None, api_secret: str | None = None, *,
    url: str = MEXC_FUTURES_SOCKET_URL,
  ):
    auth_ws = AuthedStreamsClient.new(api_key=api_key, api_secret=api_secret, url=url)
    return cls(auth_ws=auth_ws)

  async def __aenter__(self):
    await self.authenticated_ws.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.authenticated_ws.__aexit__(exc_type, exc_value, traceback)
