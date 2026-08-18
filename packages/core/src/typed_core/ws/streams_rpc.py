from typing_extensions import Literal, TypedDict, AsyncIterable, TypeVar, Generic, Any, Callable
from abc import abstractmethod
from dataclasses import dataclass, field
import asyncio

from typed_core.util import Stream, StreamManager
from .socket import Socket

Request = TypeVar('Request', default=Any)
Reply = TypeVar('Reply', default=Any)
Notification = TypeVar('Notification', default=Any)
SubscriptionParams = TypeVar('SubscriptionParams', default=Any)
SubscriptionReply = TypeVar('SubscriptionReply', default=Any)
UnsubscriptionReply = TypeVar('UnsubscriptionReply', default=Any)

class Response(TypedDict, Generic[Reply]):
  kind: Literal['response']
  id: int
  response: Reply

class Subscription(TypedDict, Generic[Notification]):
  kind: Literal['subscription']
  channel: str
  notification: Notification

Message = Response[Reply] | Subscription[Notification]

@dataclass
class StreamsRpc(Socket, Generic[Request, Reply, Notification, SubscriptionParams, SubscriptionReply, UnsubscriptionReply]):
  """Multiplexed request/response and streams socket client, via message and channel IDs.
  
  ### Features
  - Internal ID management
  - `rpc_request` for RPC request/response agnostic to IDs
  - `subscribe` to subscribe to a channel. Returns an stream manager for automatic or manual cleanup

  ### Requires implementing
  - `rpc_send` to send an identified request to the server
  - `request_subscription` to request a subscription to a channel
  - `request_unsubscription` to request an unsubscription from a channel
  - `parse_msg` to parse a message into a response/subscription

  ### Contract
  1. Connection: single owner via `async with`, also supports lazy no-owner use
  2. Requests: many concurrent `rpc_request()` calls OK
  3. Subscriptions: single `subscribe()` call supported per channel at a time
  """
  replies: dict[int, asyncio.Future[Reply]] = field(default_factory=dict, init=False, repr=False)
  counter: int = field(default=0, init=False, repr=False)
  subscriptions: dict[str, asyncio.Queue[Notification]] = field(default_factory=dict, init=False, repr=False)
  """Subscription queues, keyed by the local channel identifier."""
  message_keys: dict[str, Callable[[Notification], str]] = field(default_factory=dict, init=False, repr=False)
  """Functions to determine the local channel identifier for an incoming notification."""

  @abstractmethod
  async def rpc_send(self, id: int, req: Request, /):
    ...

  @abstractmethod
  async def request_subscription(self, channel: str, params: SubscriptionParams | None = None) -> SubscriptionReply:
    ...

  @abstractmethod
  async def request_unsubscription(self, channel: str, params: SubscriptionParams | None = None) -> UnsubscriptionReply:
    ...

  @abstractmethod
  def parse_msg(self, msg: str | bytes, /) -> Message[Reply, Notification] | None:
    ...

  async def __aexit__(self, exc_type, exc_value, traceback):
    await super().__aexit__(exc_type, exc_value, traceback)
    self.subscriptions.clear()
    self.replies.clear()

  async def rpc_request(self, request: Request) -> Reply:
    id = self.counter
    self.counter += 1
    self.replies[id] = asyncio.Future()
    await self.rpc_send(id, request)
    response = await self.wait(self.replies[id])
    del self.replies[id]
    return response

  def on_msg(self, msg: str | bytes):
    res = self.parse_msg(msg)
    if res is None:
      return
    elif res['kind'] == 'response':
      self.replies[res['id']].set_result(res['response'])
    elif res['kind'] == 'subscription':
      channel = res['channel']
      if (key := self.message_keys.get(channel)) is not None:
        channel = key(res['notification'])
      if (q := self.subscriptions.get(channel)) is not None:
        q.put_nowait(res['notification'])
    else:
      raise ValueError(f'Invalid message: {res}')

  async def _subscribe_impl(
    self,
    channel: str,
    params: SubscriptionParams | None = None,
    *,
    request_channel: str | None = None,
    message_key: Callable[[Notification], str] | None = None,
  ) -> Stream[Notification, SubscriptionReply, UnsubscriptionReply]:
    subscription_channel = request_channel or channel
    if message_key is not None:
      self.message_keys[subscription_channel] = message_key

    if channel in self.subscriptions:
      raise RuntimeError(f'Already subscribed to channel "{channel}"')

    self.subscriptions[channel] = queue = asyncio.Queue[Notification]()
    try:
      reply = await self.wait(self.request_subscription(subscription_channel, params))
    except BaseException:
      self.subscriptions.pop(channel, None)
      raise

    unsubscribed = asyncio.Future[UnsubscriptionReply]()

    async def stream() -> AsyncIterable[Notification]:
      while True:
        try:
          queue_get = asyncio.create_task(queue.get())
          done, _ = await self.wait(
            asyncio.wait([unsubscribed, queue_get], return_when='FIRST_COMPLETED')
          )
        except BaseException:
          self.subscriptions.pop(channel, None)
          raise
        if queue_get in done:
          yield queue_get.result()
        else: # unsubscribed
          break

    async def unsubscribe() -> UnsubscriptionReply | None:
      if unsubscribed.done():
        return unsubscribed.result()
      
      reply = await self.wait(self.request_unsubscription(subscription_channel, params))
      unsubscribed.set_result(reply)
      self.subscriptions.pop(channel, None)
      return reply

    return Stream(reply, stream(), unsubscribe)

  def subscribe(
    self,
    channel: str,
    params: SubscriptionParams | None = None,
    *,
    request_channel: str | None = None,
    message_key: Callable[[Notification], str] | None = None,
  ) -> StreamManager[Notification, SubscriptionReply, UnsubscriptionReply]:
    """Subscribe to a channel.

    Args:
      channel: local channel identifier
      params: optional subscription parameters
      request_channel: optional channel identifier to use for the subscription request, if different from `channel`
      message_key: optional function to derive the local channel identifier from an incoming notification. If not provided, `channel` is used to match instead
    """
    return StreamManager(lambda: self._subscribe_impl(
      channel, params, request_channel=request_channel, message_key=message_key
    ))
