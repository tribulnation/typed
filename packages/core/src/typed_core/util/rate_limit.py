from dataclasses import dataclass, field
import asyncio
import time
from collections import deque

@dataclass
class RateLimit:
  """Rate limit to `max_calls` per `period`
  
  Usage:

  ```
  limiter = RateLimit.of(5) # 5 calls/second
  for i in range(50):
    async with limiter:
      ... # do stuff, at most 5 times/second
  """
  max_calls: int
  period: float = field(kw_only=True, default=1)
  times: deque[float] = field(default_factory=deque, init=False)

  def __post_init__(self):
    self.semaphore = asyncio.Semaphore(self.max_calls)

  def _drop_expired(self, now: float | None = None):
    now = now or time.time()
    while self.times and self.times[0] < now:
      self.times.popleft()

  async def acquire(self):
    await self.semaphore.acquire()
    self._drop_expired()
    while self.times and self.times[0] >= (now := time.time()):
      wait = self.times[0] - now
      await asyncio.sleep(wait)
      self._drop_expired()
  
  async def release(self):
    ttl = time.time() + self.period
    self.times.append(ttl)
    preval = self.semaphore._value
    self.semaphore.release()

  async def __aenter__(self):
    await self.acquire()
    return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self.release()