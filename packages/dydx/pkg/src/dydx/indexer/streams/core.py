"""Shared dYdX indexer transport primitives."""

from typing_extensions import Literal, Any, NotRequired, Self, TypedDict
from dataclasses import dataclass, field
import asyncio
import logging
import orjson
import pydantic

from typed_core import LogicError, BadRequest
from typed_core.ws.streams import Streams, Subscription

logger = logging.getLogger('dydx.indexer.streams')

INDEXER_WS_URL = 'wss://indexer.dydx.trade/v4/ws'
INDEXER_TESTNET_WS_URL = 'wss://indexer.v4testnet.dydx.exchange/v4/ws'

class BaseMessage(TypedDict):
  """BaseMessage payload."""
  connection_id: str
  message_id: int

class Connected(BaseMessage):
  """Connected payload."""
  type: Literal['connected']

class Channel(TypedDict):
  """Channel payload."""
  channel: str
  id: NotRequired[str]

class Subscribed(BaseMessage, Channel):
  """Subscribed payload."""
  type: Literal['subscribed']
  contents: Any

class Unsubscribed(BaseMessage, Channel):
  """Unsubscribed payload."""
  type: Literal['unsubscribed']

class Error(BaseMessage):
  """Error payload."""
  type: Literal['error']

class Notification(BaseMessage, Channel):
  """Stream notification payload."""
  type: Literal['channel_data', 'channel_batch_data']
  version: str
  contents: Any

Msg = Connected | Subscribed | Unsubscribed | Error | Notification
MsgT: type[Msg] = Msg # type: ignore

msg_adapter = pydantic.TypeAdapter(MsgT)

class Params(TypedDict, total=False):
  """Params payload."""
  batched: bool

def parse_channel_id(channel_id: str) -> tuple[str, str|None]:
  """Split a stream channel id into channel and subscription id.

  Args:
    channel_id: Stream channel id.

  Returns:
    The parsed value.
  """
  if ':' in channel_id:
    channel, id = channel_id.split(':')
    return channel, id
  else:
    return channel_id, None

def channel_id(msg: Channel) -> str:
  """Build the local stream channel key for an indexer message.

  Args:
    msg: WebSocket message.

  Returns:
    The parsed value.
  """
  out = msg['channel']
  if (id := msg.get('id')) is not None and id != msg['channel']: # yes that happens, it's a dydx bug
    out += f':{id}'
  return out

@dataclass
class StreamsClient(Streams[Notification, Params, Subscribed, Unsubscribed]):
  """Typed-core WebSocket client for dYdX indexer streams."""
  url: str = INDEXER_WS_URL
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  replies: asyncio.Queue[Error | Subscribed | Unsubscribed] = field(default_factory=asyncio.Queue)

  def parse_msg(self, msg: str | bytes) -> Subscription | None:
    """Parse an indexer WebSocket message.
  
    Args:
      msg: WebSocket message.
  
    Returns:
      The parsed value.
    """
    obj = msg_adapter.validate_json(msg)
    match obj['type']:
      case 'subscribed' | 'unsubscribed' | 'error':
        self.replies.put_nowait(obj)
      case 'channel_data' | 'channel_batch_data':
        channel = channel_id(obj)
        return {'channel': channel, 'notification': obj}

  async def send(self, msg: object):
    """Send a WebSocket message to the indexer.
  
    Args:
      msg: WebSocket message.
    """
    ws = await self.ws
    await ws.send(orjson.dumps(msg), text=True)

  async def request(self, msg: object) -> Error | Subscribed | Unsubscribed:
    """Send a serialized WebSocket request and wait for its reply.
  
    Args:
      msg: WebSocket message.
  
    Returns:
      The subscription, unsubscription, or error reply.
    """
    async with self.lock:
      await self.send(msg)
      return await self.replies.get()

  async def request_subscription(self, channel: str, params: Params | None = None) -> Subscribed:
    """Request an indexer WebSocket subscription.
  
    Args:
      channel: Stream channel name.
      params: Query parameters.
  
    Returns:
      The parsed value.
    """
    channel, id = parse_channel_id(channel)
    msg: dict = {
      'type': 'subscribe',
      'channel': channel,
    }
    if (params or {}).get('batched', False):
      msg['batched'] = True
    if id is not None:
      msg['id'] = id
    reply = await self.request(msg)
    if reply['type'] == 'error':
      raise BadRequest(reply)
    elif reply['type'] != 'subscribed':
      raise LogicError(f'Unexpected response type: {reply}')
    return reply

  async def request_unsubscription(self, channel: str, params: Params | None = None) -> Unsubscribed:
    """Request an indexer WebSocket unsubscription.
  
    Args:
      channel: Stream channel name.
      params: Query parameters.
  
    Returns:
      The parsed value.
    """
    channel, id = parse_channel_id(channel)
    msg = {
      'type': 'unsubscribe',
      'channel': channel,
    }
    if id is not None:
      msg['id'] = id
    reply = await self.request(msg)
    if reply['type'] == 'error':
      raise BadRequest(reply)
    if reply['type'] != 'unsubscribed':
      raise LogicError(f'Unexpected response type: {reply}')
    return reply

@dataclass(kw_only=True)
class StreamsMixin:
  """Shared WebSocket indexer endpoint mixin."""
  client: StreamsClient = field(default_factory=StreamsClient)
  default_validate: bool = True

  def validate(self, validate: bool | None = None) -> bool:
    """Resolve a per-call validation override.
  
    Args:
      validate: Override the client response validation default for this call.
  
    Returns:
      The effective validation setting.
    """
    return self.default_validate if validate is None else validate

  async def __aenter__(self) -> Self:
    """Enter the indexer client context.
  
    Returns:
      The configured indexer client.
    """
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Exit the indexer client context."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  @classmethod
  def new(cls, url: str = INDEXER_WS_URL, *, validate: bool = True) -> Self:
    """Create a mainnet indexer client.
  
    Args:
      url: Indexer base URL.
      validate: Override the client response validation default for this call.
  
    Returns:
      The configured indexer client.
    """
    return cls(client=StreamsClient(url=url), default_validate=validate)
