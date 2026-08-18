from typing_extensions import (
  Any,
  Literal,
  Union,
  Annotated,
  Mapping,
  TypeAlias,
  TypeGuard,
)
from typed_core.validation import TypedDict
from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json
import logging
import websockets
from pydantic import TypeAdapter, Tag, Discriminator

from typed_core.ws.streams_rpc import StreamsRpc, Message
from typed_core.exceptions import NetworkError, ApiError

log = logging.getLogger(__name__)


class PostInfoPayload(TypedDict):
  type: str
  """Method being used"""
  data: Any
  """Actual reply you'd get from the HTTP API (yes this compulsive nesting is ridiculous)"""


class PostInfoResponse(TypedDict):
  type: Literal['info']
  payload: Any


class OtherPostResponse(TypedDict):
  type: Literal['action', 'error']
  payload: Any


PostResponse = PostInfoResponse | OtherPostResponse


class PostData(TypedDict):
  id: int
  response: PostResponse


class PostMessage(TypedDict):
  channel: Literal['post']
  data: PostData


class ErrorMessage(TypedDict):
  channel: Literal['error']
  data: Any


class PongMessage(TypedDict):
  channel: Literal['pong']


class SubscriptionResponseData(TypedDict):
  method: Literal['subscribe', 'unsubscribe']
  subscription: dict


class SubscriptionResponse(TypedDict):
  channel: Literal['subscriptionResponse']
  data: SubscriptionResponseData


class SubscriptionMessage(TypedDict):
  channel: str
  data: Any


def msg_discriminator(
  msg,
) -> Literal['post', 'subscription', 'subscriptionResponse', 'error', 'pong']:
  """Classify a raw server message for pydantic validation."""
  if isinstance(msg, Mapping):
    if msg.get('channel') == 'post':
      return 'post'
    elif msg.get('channel') == 'subscriptionResponse':
      return 'subscriptionResponse'
    elif msg.get('channel') == 'error':
      return 'error'
    elif msg.get('channel') == 'pong':
      return 'pong'
  return 'subscription'


ServerMessage: TypeAlias = Annotated[
  Union[
    Annotated[PostMessage, Tag('post')],
    Annotated[SubscriptionMessage, Tag('subscription')],
    Annotated[SubscriptionResponse, Tag('subscriptionResponse')],
    Annotated[ErrorMessage, Tag('error')],
    Annotated[PongMessage, Tag('pong')],
  ],
  Discriminator(msg_discriminator),
]
msg_adapter = TypeAdapter[
  PostMessage | SubscriptionMessage | SubscriptionResponse | ErrorMessage | PongMessage
](ServerMessage)


def is_post_msg(msg: ServerMessage) -> TypeGuard[PostMessage]:
  return msg['channel'] == 'post'


def is_subscription_response(msg: ServerMessage) -> TypeGuard[SubscriptionResponse]:
  return msg['channel'] == 'subscriptionResponse'


def is_subscription_msg(msg: ServerMessage) -> TypeGuard[SubscriptionMessage]:
  return msg_discriminator(msg) == 'subscription'


def is_error_msg(msg: ServerMessage) -> TypeGuard[ErrorMessage]:
  return msg['channel'] == 'error'


def is_pong_msg(msg: ServerMessage) -> TypeGuard[PongMessage]:
  return msg['channel'] == 'pong'


def _is_already_subscribed(data: Any) -> bool:
  return isinstance(data, str) and data.startswith('Already subscribed')


class Request(TypedDict):
  type: Literal['info', 'action']
  payload: Any


@dataclass
class SocketClient(
  StreamsRpc[
    Request, PostResponse, Any, SubscriptionResponseData, SubscriptionResponseData
  ]
):
  """Hyperliquid WebSocket transport for RPC and subscription messages."""

  ping_interval: timedelta = field(kw_only=True, default=timedelta(seconds=30))
  serial_reply: asyncio.Future[SubscriptionResponse | ErrorMessage] | None = field(
    default=None, init=False, repr=False
  )
  serial_lock: asyncio.Lock = field(
    default_factory=asyncio.Lock, init=False, repr=False
  )

  async def request_subscription(self, channel: str, params=None):
    return await self._subscription_request(
      {
        'method': 'subscribe',
        'subscription': {
          'type': channel,
          **(params or {}),
        },
      }
    )

  async def request_unsubscription(self, channel: str, params=None):
    return await self._subscription_request(
      {
        'method': 'unsubscribe',
        'subscription': {
          'type': channel,
          **(params or {}),
        },
      }
    )

  async def _subscription_request(self, payload: dict):
    async with self.serial_lock:
      self.serial_reply = asyncio.get_running_loop().create_future()
      try:
        await self.send(payload)
        msg = await self.serial_reply
      finally:
        self.serial_reply = None
    if is_subscription_response(msg):
      return msg['data']
    elif payload['method'] == 'subscribe' and _is_already_subscribed(msg['data']):
      # The ack for an earlier `subscribe` can be lost if the connection
      # drops between `send()` returning and the reply arriving (we then
      # see it as a `NetworkError` and retry) even though the server did
      # register it. The retry lands here instead: the server is telling
      # us we already have what we asked for, so treat it as success
      # rather than looping on an error that will never clear itself.
      reply: SubscriptionResponseData = {
        'method': 'subscribe',
        'subscription': payload['subscription'],
      }
      return reply
    else:
      raise ApiError(msg['data'])

  async def rpc_send(self, id: int, msg):
    return await self.send(
      {
        'method': 'post',
        'id': id,
        'request': msg,
      }
    )

  async def ping(self, ws):
    try:
      await ws.send(json.dumps({'method': 'ping'}), text=True)
    except websockets.exceptions.WebSocketException as e:
      raise NetworkError(
        'Error sending message: ping', type(e).__name__, *e.args
      ) from e

  async def send(self, msg):
    ws = await self.ws
    try:
      await ws.send(json.dumps(msg), text=True)
    except websockets.exceptions.WebSocketException as e:
      raise NetworkError(
        f'Error sending message: {msg}', type(e).__name__, *e.args
      ) from e

  def parse_msg(self, msg: str | bytes) -> Message | None:
    obj = msg_adapter.validate_json(msg)
    if is_post_msg(obj):
      return {
        'kind': 'response',
        'id': obj['data']['id'],
        'response': obj['data']['response'],
      }
    elif is_subscription_response(obj) or is_error_msg(obj):
      if self.serial_reply is not None and not self.serial_reply.done():
        self.serial_reply.set_result(obj)
      else:
        log.warning(
          'Received subscription reply with no matching request in flight: %s', obj
        )
    elif is_subscription_msg(obj):
      return {
        'kind': 'subscription',
        'channel': obj['channel'],
        'notification': obj['data'],
      }
