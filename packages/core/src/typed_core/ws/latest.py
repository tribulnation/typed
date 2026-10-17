"""Keep-latest (conflated) subscription slot, for channels whose every message is a full snapshot."""
from typing_extensions import Generic, TypeVar, Any, Callable, Literal
from dataclasses import dataclass, field
import asyncio

Notification = TypeVar('Notification', default=Any)

Pending = tuple[Literal['raw'], str | bytes] | tuple[Literal['parsed'], Notification]

@dataclass(eq=False)
class Latest(Generic[Notification]):
  """Holds only the newest message of one subscription; a newer one replaces it unread.

  A drop-in for the subscription's `asyncio.Queue` (`empty`, `put_nowait`, `get_nowait`,
  `get`), with a capacity of one that overwrites instead of blocking or growing.

  A message can arrive raw (`put_raw`, routed without decoding it) or already parsed
  (`put_nowait`, when routing had to decode it). A raw message is only parsed when the
  consumer takes it, so a message replaced before being read costs only its receive.
  """
  parse: Callable[[str | bytes], Notification]
  """Turns a raw frame routed to this subscription into its notification."""
  skipped: int = field(default=0, init=False)
  """Messages replaced by a newer one before the consumer took them."""
  pending: 'Pending[Notification] | None' = field(default=None, init=False, repr=False)
  ready: asyncio.Event = field(default_factory=asyncio.Event, init=False, repr=False)

  def store(self, item: 'Pending[Notification]'):
    """Make `item` the pending message, counting the one it replaces as skipped."""
    if self.pending is not None:
      self.skipped += 1
    self.pending = item
    self.ready.set()

  def put_raw(self, msg: str | bytes):
    """Keep a raw frame, to be parsed only if it is still the newest when taken."""
    self.store(('raw', msg))

  def put_nowait(self, notification: Notification):
    """Keep an already-parsed notification."""
    self.store(('parsed', notification))

  def empty(self) -> bool:
    """Whether no message is pending."""
    return self.pending is None

  def get_nowait(self) -> Notification:
    """Take the pending message, parsing it if it arrived raw.

    Raises:
      asyncio.QueueEmpty: No message is pending.
    """
    if self.pending is None:
      raise asyncio.QueueEmpty
    item, self.pending = self.pending, None
    self.ready.clear()
    if item[0] == 'raw':
      return self.parse(item[1])
    else:
      return item[1]

  async def get(self) -> Notification:
    """Wait for a message and take it."""
    while self.pending is None:
      await self.ready.wait()
    return self.get_nowait()
