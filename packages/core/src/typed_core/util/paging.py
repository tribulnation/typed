"""
Resumable, retry-safe pagination: a walk is a pure `next(state)` step, not a generator.

A generated `<method>_paged` returns a `PaginatedResponse` rather than an async generator
because a generator that raises is dead: nothing can retry the one page that failed and
carry on. Here every page is one call to `next(state)`, and the contract below is what
makes calling it again safe.

The contract every `next` must honour:

- `next` is a pure function of `state`. It reads no closure variable, no instance
  attribute, no clock. Calling it twice with the same `state` makes the same request.
- `state` fully determines the request. Any bound the venue would otherwise default at
  call time is pinned into `init` once, before the first page.
- The request is a read. Repeating it never changes anything on the venue.

Under that contract a caller may retry `next(state)` after a transient failure, resume a
walk from any page's `Page.next`, or run two iterations of one response concurrently,
and see exactly the pages a single uninterrupted walk would have produced.
"""
from dataclasses import dataclass, replace
from typing_extensions import (
  AsyncIterable, AsyncIterator, Awaitable, Callable, Generic, Sequence, TypeVar,
)

T = TypeVar('T')
S = TypeVar('S')


@dataclass(frozen=True)
class Page(Generic[T, S]):
  """One page of a walk, with the state on either side of it."""

  rows: Sequence[T]
  """Rows this page carried. May be empty."""
  state: S
  """State this page was fetched with. Re-fetching from it yields this page again."""
  next: S | None
  """State the following page is fetched with, or `None` when this was the last page."""


@dataclass
class PaginatedResponse(AsyncIterable[Sequence[T]], Awaitable[Sequence[T]], Generic[T, S]):
  """
  A paginated walk: `init` is the first page's state, `next` fetches one page from a
  state and returns its rows plus the following state, `None` once the walk is done.

  Awaitable (flattens every page into one list) and async-iterable (one page's rows at a
  time, empty pages skipped). `pages()` additionally exposes each page's own state, for
  checkpointing; `resume()` restarts from a saved one; `via()` routes every page fetch
  through a caller-supplied invoker, which is how a retry or logging layer wraps each
  page as one ordinary coroutine call without ever unrolling the loop by hand.

  `next` must honour the contract in this module's docstring: pure in `state`, no clock,
  read-only on the wire. Nothing here can enforce it, but everything here assumes it.

  Examples:
    ```python
    paging = client.account.trades_paged(symbol='BTCUSDT')
    trades = await paging                       # every row, flattened
    async for rows in paging: ...               # one page at a time
    async for page in paging.via(retried).pages():
      checkpoint(page.next)                     # resumable later via paging.resume(...)
    ```
  """

  init: S
  """State the first page is fetched with."""
  next: Callable[[S], Awaitable[tuple[Sequence[T], S | None]]]
  """Fetch one page: `(rows, next_state)`, `next_state` being `None` after the last page."""

  async def pages(self) -> AsyncIterator[Page[T, S]]:
    """Yield every page, empty ones included, each with the state before and after it."""
    state: S | None = self.init
    while state is not None:
      rows, following = await self.next(state)
      yield Page(rows=rows, state=state, next=following)
      state = following

  def resume(self, state: S) -> 'PaginatedResponse[T, S]':
    """
    The same walk, started from `state` instead of `init`.

    Args:
      state: A state a previous page reported as `Page.next` (or `Page.state`, to refetch
        that page itself).
    """
    return replace(self, init=state)

  def via(
    self,
    call: Callable[
      [Callable[[], Awaitable[tuple[Sequence[T], S | None]]]],
      Awaitable[tuple[Sequence[T], S | None]],
    ],
  ) -> 'PaginatedResponse[T, S]':
    """
    The same walk, with every page fetch routed through `call`.

    `call` receives a zero-argument coroutine function performing one `next(state)` and
    returns its result, so a retry policy, a logger, or any other per-call middleware
    sees each page as one plain coroutine call. Purity of `next` is what makes wrapping
    it this way safe: a retried fetch is just the same page fetched again.

    Args:
      call: Invoker applied to each page fetch, e.g. a retrying `lambda fn: fn()`.
    """
    fetch = self.next

    async def wrapped(state: S) -> tuple[Sequence[T], S | None]:
      """One page fetch, routed through `call`."""
      return await call(lambda: fetch(state))

    return replace(self, next=wrapped)

  def __aiter__(self) -> AsyncIterator[Sequence[T]]:
    async def iterate():
      """Rows of each non-empty page, in walk order."""
      async for page in self.pages():
        if page.rows:
          yield page.rows
    return iterate().__aiter__()

  def __await__(self):
    async def sync():
      """Every row of every page, flattened."""
      out: list[T] = []
      async for rows in self:
        out.extend(rows)
      return out
    return sync().__await__()
