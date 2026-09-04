"""Spot's public WebSocket connection: unauthenticated, protobuf-framed market
pushes. Also the physical socket a private (listen-key-authenticated) connection
reuses (see `.auth`): MEXC's private feed is the same endpoint with `?listenKey=...`
appended to the URL, so one `Streams` implementation serves both.
"""

from typing_extensions import TypedDict, Any
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import orjson
import pydantic

from typed_core.ws.streams import Streams, Subscription
from .proto import PushDataV3ApiWrapper

MEXC_SPOT_SOCKET_URL = 'wss://wbs-api.mexc.com/ws'


class Reply(TypedDict):
  """A command reply frame (subscribe/unsubscribe acknowledgement)."""

  id: int
  code: int
  msg: str


reply_adapter = pydantic.TypeAdapter(Reply)


@dataclass
class SpotPublicStreamsClient(Streams[PushDataV3ApiWrapper, Any, Reply, Reply]):
  """One physical Spot WebSocket v3 connection. Every push is a protobuf-encoded
  `PushDataV3ApiWrapper` frame; every reply to a subscribe/unsubscribe command is a
  small JSON frame instead -- `parse_msg` tells the two apart by attempting the JSON
  decode first."""

  url: str = field(default=MEXC_SPOT_SOCKET_URL, kw_only=True)
  ping_interval: timedelta = field(default=timedelta(seconds=15), kw_only=True)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: asyncio.Queue[Reply] = field(default_factory=asyncio.Queue, init=False, repr=False)

  async def send(self, msg):
    await (await self.ws).send(orjson.dumps(msg), text=True)

  async def send_request(self, method: str, params=None):
    msg = {'method': method}
    if params is not None:
      msg['params'] = params
    await self.send(msg)

  async def request(self, method: str, params=None):
    async with self.lock:
      await self.send_request(method, params)
      return await self.replies.get()

  async def ping(self, ws):
    await ws.send(orjson.dumps({'method': 'PING'}), text=True)

  async def request_subscription(self, channel: str, params=None) -> Reply:
    return await self.request('SUBSCRIPTION', [channel])

  async def request_unsubscription(self, channel: str, params=None) -> Reply:
    return await self.request('UNSUBSCRIPTION', [channel])

  def parse_msg(self, msg: str | bytes) -> Subscription[PushDataV3ApiWrapper] | None:
    try:
      data = reply_adapter.validate_json(msg)
      self.replies.put_nowait(data)
    except pydantic.ValidationError:
      proto = PushDataV3ApiWrapper.parse(msg)  # type: ignore
      return {'channel': proto.channel, 'notification': proto}
