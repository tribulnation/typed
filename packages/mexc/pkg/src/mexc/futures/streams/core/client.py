from typing_extensions import Any, TypedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import orjson

from typed_core.ws.streams import Streams, Subscription
from mexc.core import validator, ValidationMixin

MEXC_FUTURES_SOCKET_URL = 'wss://contract.mexc.com/edge'

class Reply(TypedDict):
  channel: str
  data: Any
  ts: datetime

validate_reply = validator(Reply)

@dataclass
class StreamsClient(Streams[Any, Any, Reply, Reply]):
  url: str = field(default=MEXC_FUTURES_SOCKET_URL, kw_only=True)
  ping_interval: timedelta = field(default=timedelta(seconds=15), kw_only=True)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: asyncio.Queue[Reply] = field(default_factory=asyncio.Queue, init=False)

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

  async def request_subscription(self, channel: str, params=None):
    return await self.request(f'sub.{channel}', params)

  async def request_unsubscription(self, channel: str, params=None):
    return await self.request(f'unsub.{channel}')

  def parse_msg(self, msg: str | bytes) -> Subscription[Any] | None:
    r = validate_reply(msg)
    if r['channel'].startswith('push.'):
      channel = r['channel'].removeprefix('push.')
      if channel == 'depth' and channel not in self.subscriptions and 'depth.full' in self.subscriptions:
        channel = 'depth.full'
      return {'channel': channel, 'notification': r['data']}
    else:
      self.replies.put_nowait(r)
    
@dataclass
class StreamsMixin(ValidationMixin):
  ws: StreamsClient

  @classmethod
  def public(
    cls, *, url: str = MEXC_FUTURES_SOCKET_URL,
    default_validate: bool = True,
  ):
    ws = StreamsClient(url=url)
    return cls(ws=ws, default_validate=default_validate)

  async def __aenter__(self):
    await self.ws.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.ws.__aexit__(exc_type, exc_value, traceback)

  async def subscribe(self, channel: str, params=None):
    return await self.ws.subscribe(channel, params)
