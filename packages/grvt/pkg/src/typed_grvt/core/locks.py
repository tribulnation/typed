"""An `asyncio.Lock` that never binds a client to the first event loop it ran on."""

from dataclasses import dataclass, field
import asyncio
import weakref


@dataclass
class LoopLock:
  """A mutual-exclusion lock with one `asyncio.Lock` per running event loop.

  An `asyncio.Lock` binds itself to the loop of its first contended acquire, so a client
  holding one breaks under a second `asyncio.run` once that lock was ever contended (a
  re-login raced by two calls, say). A `LoopLock` creates its lock lazily for whichever loop
  is running, and forgets it with the loop. Exclusion is per loop, which is all a client
  needs: two loops never share one client at the same time.
  """

  locks: 'weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock]' = field(
    default_factory=weakref.WeakKeyDictionary, init=False, repr=False
  )

  @property
  def lock(self) -> asyncio.Lock:
    """The running loop's lock, created on first use."""
    loop = asyncio.get_running_loop()
    if (lock := self.locks.get(loop)) is None:
      lock = self.locks[loop] = asyncio.Lock()
    return lock

  async def __aenter__(self):
    """Acquire the running loop's lock."""
    await self.lock.acquire()

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release the running loop's lock."""
    self.lock.release()
