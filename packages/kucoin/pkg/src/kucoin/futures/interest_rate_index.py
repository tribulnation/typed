"""`GET /api/v1/interest/query` — Get Interest Rate Index."""

from typing_extensions import AsyncIterator
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesInterestRateSnapshot(TypedDict):
  """One index snapshot."""

  symbol: str
  """Interest index symbol, e.g. `.XBTINT` (see `futures.symbol`'s `fundingBaseSymbol1M`/`fundingQuoteSymbol1M` fields for a given contract)."""
  granularity: int
  """Snapshot interval, milliseconds. A raw interval value, not a documented closed set of categories -- left bare rather than an enum, observed `60000` (1 minute) live."""
  timePoint: int
  """Snapshot timestamp, Unix ms."""
  value: float
  """Index value at this point."""


class FuturesInterestRateSnapshotPage(TypedDict):
  """One page of index history."""

  dataList: list[FuturesInterestRateSnapshot]
  """Index snapshots, newest first."""
  hasMore: bool
  """Whether more historical records exist beyond this page."""


_Type = FuturesInterestRateSnapshotPage
adapter = validator[_Type](_Type)  # type: ignore


class InterestRateIndex(RpcEndpoint):
  """`Get Interest Rate Index` — mixed into `Futures`, the product exposing `futures.interest_rate_index`."""

  async def interest_rate_index(
    self,
    *,
    symbol: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    reverse: bool | None = None,
    offset: int | None = None,
    forward: bool | None = None,
    max_count: int | None = None,
    validate: bool | None = None,
  ) -> FuturesInterestRateSnapshotPage:
    """Get the interest rate index used in a futures contract's funding rate calculation, either the current snapshot or a historical window.

    Args:
      symbol: Interest index symbol, e.g. `.XBTINT` (see `futures.symbol`'s `fundingBaseSymbol1M`/`fundingQuoteSymbol1M` fields for a given contract).
      start_at: Start of the window, Unix ms. Inclusive -- confirmed live (see notes).
      end_at: End of the window, Unix ms. Inclusive -- confirmed live (see notes).
      reverse: Reverse the sort order of results. Not independently verified live -- documented, left as-is.
      offset: Continuation offset for an alternative (undocumented-shape) paging mode -- see notes; this spec models the `startAt`/`endAt` bounded-window mode instead.
      forward: Direction for offset-based paging -- see `offset`.
      max_count: Maximum records to return. Confirmed live default `10` (an unfiltered call with no `maxCount` returned exactly 10 rows).
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if start_at is not None:
      params['startAt'] = start_at
    if end_at is not None:
      params['endAt'] = end_at
    if reverse is not None:
      params['reverse'] = reverse
    if offset is not None:
      params['offset'] = offset
    if forward is not None:
      params['forward'] = forward
    if max_count is not None:
      params['maxCount'] = max_count
    return await self.request(
      'GET',
      '/api/v1/interest/query',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def interest_rate_index_paged(
    self,
    *,
    symbol: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    reverse: bool | None = None,
    offset: int | None = None,
    forward: bool | None = None,
    max_count: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[FuturesInterestRateSnapshotPage]:
    """Yield successive pages of `interest_rate_index`.

    Moves the `start_at`–`end_at` window forwards by its own width and stops on the
    first empty window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `start_at` and `end_at` state, so
    choose a window the venue answers in one response: it caps a wider one, and the walk
    moves past the rows that were left out.
    """
    if start_at is None or end_at is None:
      raise ValueError(
        '`interest_rate_index_paged` walks a time window: pass both `start_at` and `end_at`'
      )
    lower = start_at
    upper = end_at
    width = upper - lower
    pages = 0
    while True:
      response = await self.interest_rate_index(
        symbol=symbol,
        start_at=lower,
        end_at=upper,
        reverse=reverse,
        offset=offset,
        forward=forward,
        max_count=max_count,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('dataList') if response is not None else None
      if not rows:
        break
      lower = upper + 1
      upper = lower + width
