"""`GET /v5/market/funding/history` — Get Funding Rate History."""

from typing_extensions import AsyncIterator, Literal, TypedDict
from bybit.core import Endpoint, validator
from typed_core.exceptions import LogicError


class FundingRate(TypedDict):
  """One settled funding rate."""

  symbol: str
  """Symbol name."""
  fundingRate: str
  """Funding rate charged at the settlement, as a ratio."""
  fundingRateTimestamp: str
  """Settlement time, as a millisecond timestamp."""


class FundingRateHistory(TypedDict):
  """Settled funding rates for one contract."""

  category: Literal['linear', 'inverse']
  """Product type."""
  list: list[FundingRate]
  """Funding settlements, sorted by settlement time in descending order."""


adapter = validator[FundingRateHistory](FundingRateHistory)


class FundingHistory(Endpoint):
  """`Get Funding Rate History` — mixed into the router that owns `market.funding_history`."""

  async def funding_history(
    self,
    *,
    category: Literal['linear', 'inverse'],
    symbol: str,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> FundingRateHistory:
    """Get settled funding rates for a perpetual contract, newest first. Bybit returns the rates that were actually charged, so the series is bounded by `startTime`, `endTime` and `limit`.

    Args:
      category: Product type.
      symbol: Symbol name in uppercase, for example `BTCUSDT`.
      start_time: Start of the queried range, as a millisecond timestamp.
      end_time: End of the queried range, as a millisecond timestamp.
      limit: Number of settlements per page. Range [1, 200]; defaults to 200.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/history-fund-rate)
    """
    params: dict = {
      'category': category,
      'symbol': symbol,
    }
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', '/v5/market/funding/history', params=params)
    return self.result(r, adapter, validate)

  async def funding_history_paged(
    self,
    *,
    category: Literal['linear', 'inverse'],
    symbol: str,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    allow_truncation: bool = False,
    validate: bool | None = None,
  ) -> AsyncIterator[FundingRateHistory]:
    """Yield successive pages of `funding_history`.

    Moves the `start_time`–`end_time` window backwards by its own width and stops on the
    first empty window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `start_time` and `end_time` state, so
    choose a window the venue answers in one response — at most `limit` rows. A full
    page is evidence the window was capped, and raises `LogicError` rather than walking
    past the rows that were left out; pass `allow_truncation=True` to accept the loss
    and keep going.
    """
    if start_time is None or end_time is None:
      raise ValueError(
        '`funding_history_paged` walks a time window: pass both `start_time` and `end_time`'
      )
    lower = start_time
    upper = end_time
    width = upper - lower
    pages = 0
    while True:
      response = await self.funding_history(
        category=category,
        symbol=symbol,
        start_time=lower,
        end_time=upper,
        limit=limit,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('list')
      if not rows:
        break
      if not allow_truncation and len(rows) >= (limit if limit is not None else 200):
        raise LogicError(
          f'`funding_history_paged` requested the window {lower} to {upper} and the venue returned a full page of {len(rows)} rows, so it may hold more; advancing would move past the rows that were left out. Narrow the window, or pass `allow_truncation=True` to accept the loss.'
        )
      upper = lower - 1
      lower = upper - width
