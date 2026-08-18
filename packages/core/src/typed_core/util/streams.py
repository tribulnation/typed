from typing_extensions import AsyncIterable, Generic, Awaitable, Callable, TypeVar, Any
from dataclasses import dataclass, field, replace

T = TypeVar('T', default=Any)
Notification = TypeVar('Notification', default=Any)
SubscriptionReply = TypeVar('SubscriptionReply', default=Any)
UnsubscriptionReply = TypeVar('UnsubscriptionReply', default=Any)

@dataclass
class Stream(AsyncIterable[Notification], Generic[Notification, SubscriptionReply, UnsubscriptionReply]):
  """Represents a subscription to a stream.
  
  Usage:

  ```python
  print(stream.reply)
  async for msg in stream:
    ...
  await stream.unsubscribe()
  ```
  """
  reply: SubscriptionReply
  stream: AsyncIterable[Notification]
  unsubscribe: Callable[[], Awaitable[UnsubscriptionReply | None]]

  def __aiter__(self):
    return self.stream.__aiter__()
  
  def map(self, f: Callable[[Notification], T]) -> 'Stream[T, SubscriptionReply, UnsubscriptionReply]':
    async def stream() -> AsyncIterable[T]:
      async for msg in self.stream:
        yield f(msg)
    return replace(self, stream=stream()) # type: ignore

  def filter(self, f: Callable[[Notification], bool]) -> 'Stream[Notification, SubscriptionReply, UnsubscriptionReply]':
    async def stream() -> AsyncIterable[Notification]:
      async for msg in self.stream:
        if f(msg):
          yield msg
    return replace(self, stream=stream())


@dataclass
class StreamManager(AsyncIterable[Notification], Generic[Notification, SubscriptionReply, UnsubscriptionReply]):
  """Manages a subscription to a stream, allowing for these two usage patterns:
  
  1. Legacy/simple `await` usage:

    ```
    stream = await manager
    async for msg in stream:
      ...
    await stream.unsubscribe()
    ```

  2. Context manager with automated cleanup:

    ```
    async with manager as stream:
      async for msg in stream:
        ...
    # auto unsubscribed on exit
    ```
  """
  connect: Callable[[], Awaitable[Stream[Notification, SubscriptionReply, UnsubscriptionReply]]]
  stream: Stream[Notification, SubscriptionReply, UnsubscriptionReply] | None = None

  def __await__(self):
    return self.connect().__await__()
  
  def __aiter__(self):
    if self.stream is None:
      raise RuntimeError('Subscription not connected yet. Use with await or async with.')
    return self.stream.__aiter__()

  async def __aenter__(self):
    self.stream = await self.connect()
    return self.stream
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    if self.stream is not None:
      await self.stream.unsubscribe()
    self.stream = None

  def map(self, f: Callable[[Notification], T]) -> 'StreamManager[T, SubscriptionReply, UnsubscriptionReply]':
    async def connect() -> Stream[T, SubscriptionReply, UnsubscriptionReply]:
      stream = await self.connect()
      return stream.map(f)
    return StreamManager(connect=connect)

  def filter(self, f: Callable[[Notification], bool]) -> 'StreamManager[Notification, SubscriptionReply, UnsubscriptionReply]':
    async def connect() -> Stream[Notification, SubscriptionReply, UnsubscriptionReply]:
      stream = await self.connect()
      return stream.filter(f)
    return StreamManager(connect=connect)