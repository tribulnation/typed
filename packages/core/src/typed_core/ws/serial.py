from typing_extensions import Any, TypeVar, Generic
from abc import abstractmethod
from dataclasses import dataclass, field
import asyncio

Reply = TypeVar('Reply', default=Any)

@dataclass
class SerialReplies(Generic[Reply]):
  """Mixin for a connection whose replies carry no correlation id.

  Serializes each request under a lock and matches it to the very next reply, by
  arrival order alone — the only correlation a venue like this gives you.

  ### Features
  - `request` to send one message and await its reply, serialized against every other
    concurrent `request()` call on the same connection

  ### Requires implementing
  - `send` to write one message to the wire

  Route a parsed reply into `self.replies.put_nowait(...)` — from `parse_msg`
  (`Streams`/`StreamsRpc`) or `parse_response` (`Rpc`), whichever this is composed
  with — and return `None`/skip it there; this class never parses incoming messages
  itself, it only fulfills replies routed to it.

  Compose alongside `Streams`, `Rpc`, or `StreamsRpc` (whichever actually owns the
  connection) rather than instead of one: this only adds `request`, `replies` and
  `lock`, it never overrides anything they define, so a venue can mix correlation
  strategies freely — an id-correlated `Rpc` surface and an uncorrelated
  subscribe/unsubscribe surface on the very same connection both work. The combining
  subclass needs its own `@dataclass` (same as `Streams`/`Rpc`/`StreamsRpc` themselves
  do over `Socket`) for the merged fields to resolve into one `__init__`.

  ### Concurrency Contract
  1. Requests: many concurrent `request()` calls OK, serialized internally
  """
  replies: asyncio.Queue[Reply] = field(default_factory=asyncio.Queue, init=False, repr=False)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  @abstractmethod
  async def send(self, msg: object):
    ...

  async def request(self, msg: object) -> Reply:
    """Send `msg` and return the next reply, serialized against concurrent callers.

    Args:
      msg: Message to send.
    """
    async with self.lock:
      await self.send(msg)
      return await self.replies.get()
