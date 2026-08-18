"""`GET /v5/market/account-ratio` — Get Long Short Ratio."""

from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from bybit.types import MetricInterval
from bybit.core import Endpoint, validator


class LongShortRatio(TypedDict):
  """One long/short account ratio sample."""

  symbol: str
  """Symbol name."""
  buyRatio: str
  """Share of accounts holding a long position, as a ratio."""
  sellRatio: str
  """Share of accounts holding a short position, as a ratio."""
  timestamp: str
  """Sample time, as a millisecond timestamp."""


class LongShortRatioResult(TypedDict):
  """Long/short account ratio series."""

  list: list[LongShortRatio]
  """Ratio samples, sorted by timestamp in descending order."""
  nextPageCursor: NotRequired[str]
  """Opaque cursor for the next page. Pass it back as `cursor`; an empty string means there are no further pages."""


adapter = validator[LongShortRatioResult](LongShortRatioResult)


class LongShortRatioEndpoint(Endpoint):
  """`Get Long Short Ratio` — mixed into the router that owns `market.long_short_ratio`."""

  async def long_short_ratio(
    self,
    *,
    category: Literal['linear', 'inverse'],
    symbol: str,
    period: MetricInterval,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    cursor: str | None = None,
    validate: bool | None = None,
  ) -> LongShortRatioResult:
    """Get the ratio of accounts holding long versus short positions in a contract, sampled at a fixed interval and newest first.

    Args:
      category: Product type.
      symbol: Symbol name in uppercase, for example `BTCUSDT`.
      period: Sampling interval of the series.
      start_time: Start of the queried range, as a millisecond timestamp.
      end_time: End of the queried range, as a millisecond timestamp.
      limit: Number of samples per page. Range [1, 500]; defaults to 50.
      cursor: Opaque pagination cursor. Pass the `nextPageCursor` returned by the previous page; omit it for the first page.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/long-short-ratio)
    """
    params: dict = {
      'category': category,
      'symbol': symbol,
      'period': period,
    }
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    if cursor is not None:
      params['cursor'] = cursor
    r = await self.request('GET', '/v5/market/account-ratio', params=params)
    return self.result(r, adapter, validate)

  async def long_short_ratio_paged(
    self,
    *,
    category: Literal['linear', 'inverse'],
    symbol: str,
    period: MetricInterval,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[LongShortRatioResult]:
    """Yield successive pages of `long_short_ratio`.

    Passes each page's token back as `cursor` and stops when a response carries no
    `nextPageCursor`, or after `max_pages` pages when one is given.
    """
    cursor: str | None = None
    pages = 0
    while True:
      response = await self.long_short_ratio(
        category=category,
        symbol=symbol,
        period=period,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        cursor=cursor,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      cursor = response.get('nextPageCursor')
      if not cursor:
        break
