"""
Pins `PaginatedResponse`'s resumable, retry-safe contract: every page is one pure
`next(state)` call, so a page can be retried, a walk resumed from any page's state, and a
per-call invoker (`via`) wrapped around each fetch without unrolling the loop by hand.
"""
import pytest

from typed_core.util.paging import Page, PaginatedResponse


def counting(pages: dict[int, list[str]]):
  """A walk over integer states `1..len(pages)`, recording every `next` call."""
  calls: list[int] = []

  async def next(state: int) -> tuple[list[str], int | None]:
    calls.append(state)
    following = state + 1 if state + 1 in pages else None
    return pages[state], following

  return PaginatedResponse(1, next), calls


@pytest.mark.asyncio
async def test_await_flattens_every_page():
  paging, _ = counting({1: ['a', 'b'], 2: [], 3: ['c']})
  assert await paging == ['a', 'b', 'c']


@pytest.mark.asyncio
async def test_aiter_skips_empty_pages():
  paging, _ = counting({1: ['a', 'b'], 2: [], 3: ['c']})
  assert [rows async for rows in paging] == [['a', 'b'], ['c']]


@pytest.mark.asyncio
async def test_pages_yields_every_page_with_its_states():
  """Empty pages included: a checkpoint needs every state transition, not only the
  ones that carried rows."""
  paging, _ = counting({1: ['a'], 2: [], 3: ['c']})
  assert [page async for page in paging.pages()] == [
    Page(rows=['a'], state=1, next=2),
    Page(rows=[], state=2, next=3),
    Page(rows=['c'], state=3, next=None),
  ]


@pytest.mark.asyncio
async def test_resume_starts_from_a_saved_state():
  paging, calls = counting({1: ['a'], 2: ['b'], 3: ['c']})
  assert await paging.resume(2) == ['b', 'c']
  assert calls == [2, 3]


@pytest.mark.asyncio
async def test_via_routes_every_fetch_through_the_invoker():
  paging, _ = counting({1: ['a'], 2: ['b']})
  seen: list[str] = []

  async def call(fn):
    """A stand-in for a retry/log middleware: sees one coroutine call per page."""
    seen.append('fetch')
    return await fn()

  assert await paging.via(call) == ['a', 'b']
  assert seen == ['fetch', 'fetch']


@pytest.mark.asyncio
async def test_via_lets_the_invoker_retry_one_page():
  """The whole point: a transient failure on page two is retried at page two, and page
  one is never fetched again."""
  attempts: list[int] = []

  async def next(state: int) -> tuple[list[str], int | None]:
    attempts.append(state)
    if state == 2 and attempts.count(2) == 1:
      raise ConnectionError('transient')
    return [str(state)], state + 1 if state < 3 else None

  async def retried(fn):
    """Retry once on `ConnectionError`."""
    try:
      return await fn()
    except ConnectionError:
      return await fn()

  paging = PaginatedResponse(1, next)
  assert await paging.via(retried) == ['1', '2', '3']
  assert attempts == [1, 2, 2, 3]


@pytest.mark.asyncio
async def test_via_and_resume_leave_the_original_untouched():
  paging, calls = counting({1: ['a'], 2: ['b']})
  resumed = paging.resume(2)
  wrapped = paging.via(lambda fn: fn())
  assert paging.init == 1 and resumed.init == 2
  assert wrapped.next is not paging.next
  assert await paging == ['a', 'b']
  assert calls == [1, 2]


@pytest.mark.asyncio
async def test_two_iterations_share_no_state():
  """`next` is pure in `state`, so nothing about one iteration leaks into another."""
  paging, calls = counting({1: ['a'], 2: ['b']})
  first = [rows async for rows in paging]
  second = [rows async for rows in paging]
  assert first == second == [['a'], ['b']]
  assert calls == [1, 2, 1, 2]
