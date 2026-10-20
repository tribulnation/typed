"""Shared ownership of connections, counted so that no cancellation can unbalance it.

Several `async with` blocks own the same connections at once (the whole client, each surface,
the transports sharing the session and the market-data gateway), so each object holding
connections counts its owners and closes them when the last one leaves. The counting is
synchronous, done before anything is awaited, so a task cancelled while entering or leaving
never leaves a count behind; and the closes a last exit starts always run to completion.
"""

from collections.abc import Sequence
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass, field
import asyncio

from typing_extensions import Any, Self

Connection = AbstractAsyncContextManager[Any]
"""A connection an owned object holds alone: a `typed_core` `HttpClient` or `Socket`."""


async def close(
  connections: Sequence[Connection], exc_type=None, exc_value=None, traceback=None
):
  """Exit `connections` concurrently, to completion even if the caller is cancelled meanwhile.

  A cancellation that lands while they close is re-raised once every close is done, so a
  cancelled exit still leaves nothing open. Otherwise the first close that failed is raised,
  after the others finished.
  """
  if not connections:
    return
  closing = asyncio.gather(
    *(c.__aexit__(exc_type, exc_value, traceback) for c in connections),
    return_exceptions=True,
  )
  cancelled: asyncio.CancelledError | None = None
  while not closing.done():
    try:
      # `wait` never cancels `closing`: a cancellation here only interrupts the waiting,
      # which then resumes.
      await asyncio.wait([closing])
    except asyncio.CancelledError as e:
      cancelled = e
  if cancelled is not None:
    raise cancelled
  for result in closing.result():
    if isinstance(result, BaseException):
      raise result


@dataclass(kw_only=True)
class Owned:
  """Connections that several `async with` blocks own at once, closed when the last leaves.

  `connections()` are what this object holds alone; `shared()` are other owned objects it
  takes one ownership of for as long as it is owned itself (a transport's session, say). One
  `async with` counts one owner here and, recursively, in everything shared, all
  synchronously before its first await; the exit counts it out the same way and then closes
  the connections of every object whose last owner just left, together (`close`).

  A connection itself is entered only by an object's first owner and exited by its last:
  `typed_core`'s `HttpClient` and `Socket` take ownership without connecting and open
  lazily, so entering one does nothing a cancellation could interrupt, and an enter that
  fails or is cancelled anyway counts its owner back out before raising.

  A subclass lists `Owned` before any `Protocol` it implements, so these `__aenter__`/
  `__aexit__` win over the protocol's stubs.
  """

  owners: int = field(default=0, init=False, repr=False)
  """Open `async with` blocks on this object, directly or through one sharing it."""

  def connections(self) -> Sequence[Connection]:
    """Connections this object holds alone, closed when its last owner leaves."""
    return ()

  def shared(self) -> Sequence['Owned']:
    """Owned objects this one takes one ownership of while it is owned itself."""
    return ()

  def acquire(self) -> list[Connection]:
    """Count one owner in, here and in everything shared, synchronously.

    Returns:
      The connections to enter: those of every object this made the first owner of.
    """
    self.owners += 1
    opening = list(self.connections()) if self.owners == 1 else []
    for other in self.shared():
      opening += other.acquire()
    return opening

  def release(self) -> list[Connection]:
    """Count one owner out, here and in everything shared, synchronously.

    An exit with no owner left (a client used without `async with`, then exited) still
    closes this object's connections, which reopen lazily on next use.

    Returns:
      The connections to close: those of every object whose last owner just left.
    """
    self.owners = max(0, self.owners - 1)
    closing = [] if self.owners else list(self.connections())
    for other in self.shared():
      closing += other.release()
    return closing

  async def __aenter__(self) -> Self:
    """Take one ownership of the connections; each opens lazily on first use."""
    opening = self.acquire()
    try:
      for connection in opening:
        await connection.__aenter__()
    except BaseException:
      await close(self.release())
      raise
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release this ownership; the connections whose last owner left are closed."""
    await close(self.release(), exc_type, exc_value, traceback)
