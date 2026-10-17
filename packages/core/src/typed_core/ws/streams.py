from typing_extensions import TypedDict, AsyncIterable, TypeVar, Generic, Any, Callable
from abc import abstractmethod
from dataclasses import dataclass, field
import asyncio

from typed_core.util import Stream, StreamManager
from typed_core.exceptions import NetworkError
from .latest import Latest
from .socket import Context, Socket

Notification = TypeVar('Notification', default=Any)
SubscriptionParams = TypeVar('SubscriptionParams', default=Any)
SubscriptionReply = TypeVar('SubscriptionReply', default=Any)
UnsubscriptionReply = TypeVar('UnsubscriptionReply', default=Any)

class Subscription(TypedDict, Generic[Notification]):
  channel: str
  notification: Notification

@dataclass
class Streams(Socket, Generic[Notification, SubscriptionParams, SubscriptionReply, UnsubscriptionReply]):
  """Multiplex subscribe/stream client (supports multiple concurrent subscriptions).
  
  ### Features
  - Subscriptions management
  - `subscribe` to subscribe to a channel. Returns an stream manager for automatic or manual cleanup

  ### Requires implementing
  - `request_subscription` to request a subscription to a channel
  - `request_unsubscription` to request an unsubscription from a channel
  - `parse_msg` to parse a message into a subscription

  ### Contract
  1. Connection: single owner via `async with`, also supports lazy no-owner use
  2. Subscriptions: single `subscribe()` call supported per channel at a time
  """
  subscriptions: dict[str, asyncio.Queue[Notification] | Latest[Notification]] = field(default_factory=dict, init=False, repr=False)
  """Subscription queues, keyed by the local channel identifier."""
  latest: dict[str, Latest[Notification]] = field(default_factory=dict, init=False, repr=False)
  """The keep-latest subscriptions among `subscriptions`, for raw routing via `route_raw`."""
  message_keys: dict[str, Callable[[Notification], str]] = field(default_factory=dict, init=False, repr=False)
  """Functions to determine the local channel identifier for an incoming notification."""

  @abstractmethod
  async def request_subscription(self, channel: str, params: SubscriptionParams | None = None) -> SubscriptionReply:
    ...

  @abstractmethod
  async def request_unsubscription(self, channel: str, params: SubscriptionParams | None = None) -> UnsubscriptionReply:
    ...

  @abstractmethod
  def parse_msg(self, msg: str | bytes) -> Subscription[Notification] | None:
    ...

  def route_raw(self, msg: str | bytes, /) -> str | None:
    """Name the keep-latest subscription a frame belongs to without decoding it, if that is cheap.

    Only called while a `keep_latest` subscription exists. Return the *local* channel
    identifier (what `subscribe` was given as `channel`, after any `message_key`), and
    only when sure: the frame is then kept raw and parsed by `parse_msg` only if it is
    still the newest when the consumer reads it. Return `None` to route by `parse_msg`
    as usual -- always correct, but skipped frames then still pay the decode (never the
    validation, which runs on read). The default never routes raw.
    """

  def parse_notification(self, msg: str | bytes, /) -> Notification:
    """Parse a frame `route_raw` routed, read from a keep-latest subscription.

    Raises:
      ValueError: `parse_msg` does not read the frame as a subscription notification.
    """
    res = self.parse_msg(msg)
    if res is not None:
      return res['notification']
    else:
      raise ValueError(f'Frame routed raw is not a subscription notification: {msg!r}')

  async def __aexit__(self, exc_type, exc_value, traceback):
    await super().__aexit__(exc_type, exc_value, traceback)
    self.subscriptions.clear()

  def connection_closed(self, ctx: Context):
    """Forget the closed connection's subscriptions; its streams raise `NetworkError`."""
    self.subscriptions.clear()
    self.latest.clear()
    self.message_keys.clear()
    super().connection_closed(ctx)

  def on_msg(self, msg: str | bytes):
    if self.latest and (channel := self.route_raw(msg)) is not None and (slot := self.latest.get(channel)) is not None:
      slot.put_raw(msg)
      return
    res = self.parse_msg(msg)
    if res is not None:
      channel = res['channel']
      if (key := self.message_keys.get(channel)) is not None:
        channel = key(res['notification'])
      if (q := self.subscriptions.get(channel)) is not None:
        q.put_nowait(res['notification'])

  async def _subscribe_impl(
    self,
    channel: str,
    params: SubscriptionParams | None = None,
    *,
    request_channel: str | None = None,
    message_key: Callable[[Notification], str] | None = None,
    keep_latest: bool = False,
  ) -> Stream[Notification, SubscriptionReply, UnsubscriptionReply]:
    subscription_channel = request_channel or channel
    # Resolved first: a dead connection is discarded here, with its subscriptions.
    ctx = await self.ctx

    if channel in self.subscriptions:
      raise RuntimeError(f'Already subscribed to channel "{channel}"')
    if message_key is not None:
      self.message_keys[subscription_channel] = message_key

    queue: asyncio.Queue[Notification] | Latest[Notification]
    if keep_latest:
      queue = self.latest[channel] = Latest(self.parse_notification)
    else:
      queue = asyncio.Queue[Notification]()
    self.subscriptions[channel] = queue

    def forget():
      """Drop this stream's queue, unless the channel was since subscribed anew."""
      if self.subscriptions.get(channel) is queue:
        del self.subscriptions[channel]
      if self.latest.get(channel) is queue:
        del self.latest[channel]

    try:
      reply = await self.wait(self.request_subscription(subscription_channel, params), ctx=ctx)
    except BaseException:
      forget()
      raise

    unsubscribed = asyncio.Future[UnsubscriptionReply | None]()

    async def stream() -> AsyncIterable[Notification]:
      while True:
        # What arrived before a drop is still delivered, before the drop is raised.
        if not queue.empty():
          yield queue.get_nowait()
          continue
        if unsubscribed.done():
          break
        queue_get = asyncio.ensure_future(queue.get())
        try:
          done, _ = await self.wait(
            asyncio.wait([unsubscribed, queue_get], return_when='FIRST_COMPLETED'), ctx=ctx
          )
        except BaseException:
          forget()
          raise
        finally:
          queue_get.cancel()
          await asyncio.gather(queue_get, return_exceptions=True)
        if queue_get in done:
          yield queue_get.result()
        else: # unsubscribed
          break

    async def unsubscribe() -> UnsubscriptionReply | None:
      """Unsubscribe on the connection the stream was made on; a no-op once it is gone."""
      if unsubscribed.done():
        return unsubscribed.result()
      reply = None
      try:
        if ctx.alive:
          try:
            reply = await self.wait(self.request_unsubscription(subscription_channel, params), ctx=ctx)
          except NetworkError:
            if ctx.alive:
              raise
        return reply
      finally:
        if not unsubscribed.done():
          unsubscribed.set_result(reply)
        forget()

    if isinstance(queue, Latest):
      return Stream(reply, stream(), unsubscribe, skipped_count=lambda: queue.skipped)
    else:
      return Stream(reply, stream(), unsubscribe)


  def subscribe(
    self,
    channel: str,
    params: SubscriptionParams | None = None,
    *,
    request_channel: str | None = None,
    message_key: Callable[[Notification], str] | None = None,
    keep_latest: bool = False,
  ) -> StreamManager[Notification, SubscriptionReply, UnsubscriptionReply]:
    """Subscribe to a channel.

    Args:
      channel: local channel identifier
      params: optional subscription parameters
      request_channel: optional channel identifier to use for the subscription request, if different from `channel`
      message_key: optional function to derive the local channel identifier from an incoming notification. If not provided, `channel` is used to match instead
      keep_latest: deliver only the newest message: one arriving before the previous was read replaces it, counted in the stream's `skipped`. Only for channels whose every message is a full snapshot (best bid/ask, partial depth, mark price), never for diffs, trades, fills or account events. Frames `route_raw` can route are kept raw and parsed on read; a frame that then fails to parse raises from the read (ending that stream) instead of failing the connection. The default delivers every message, in order
    """
    return StreamManager(lambda: self._subscribe_impl(
      channel, params, request_channel=request_channel, message_key=message_key,
      keep_latest=keep_latest,
    ))
