"""`GET /v5/market/premium-index-price-kline` — Get Premium Index Price Kline."""

from typing_extensions import AsyncIterator, Literal, TypedDict
from bybit.types import KlineInterval
from bybit.core import Endpoint, validator
from typed_core.exceptions import LogicError


class PremiumIndexPriceKlineResult(TypedDict):
  """Candle series for one symbol."""

  category: Literal['linear', 'inverse']
  """Product type the candles belong to."""
  symbol: str
  """Symbol name."""
  list: list[tuple[str, str, str, str, str]]
  """Candles, sorted by start time in descending order."""


adapter = validator[PremiumIndexPriceKlineResult](PremiumIndexPriceKlineResult)


class PremiumIndexPriceKline(Endpoint):
  """`Get Premium Index Price Kline` — mixed into the router that owns `market.premium_index_price_kline`."""

  async def premium_index_price_kline(
    self,
    *,
    category: Literal['linear', 'inverse'] | None = None,
    symbol: str,
    interval: KlineInterval,
    start: int | None = None,
    end: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PremiumIndexPriceKlineResult:
    """Get premium index price candles for a contract. The premium index drives the funding rate, so values are small signed ratios rather than prices.

    Args:
      category: Product type. Defaults to `linear` when omitted.
      symbol: Symbol name in uppercase, for example `BTCUSDT`.
      interval: Candle duration.
      start: Start of the queried range, as a millisecond timestamp.
      end: End of the queried range, as a millisecond timestamp.
      limit: Number of candles per page. Range [1, 1000]; defaults to 200.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/premium-index-kline)
    """
    params: dict = {
      'symbol': symbol,
      'interval': interval,
    }
    if category is not None:
      params['category'] = category
    if start is not None:
      params['start'] = start
    if end is not None:
      params['end'] = end
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', '/v5/market/premium-index-price-kline', params=params)
    return self.result(r, adapter, validate)

  async def premium_index_price_kline_paged(
    self,
    *,
    category: Literal['linear', 'inverse'] | None = None,
    symbol: str,
    interval: KlineInterval,
    start: int | None = None,
    end: int | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    allow_truncation: bool = False,
    validate: bool | None = None,
  ) -> AsyncIterator[PremiumIndexPriceKlineResult]:
    """Yield successive pages of `premium_index_price_kline`.

    Moves the `start`–`end` window backwards by its own width and stops on the first
    empty window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `start` and `end` state, so choose a
    window the venue answers in one response — at most `limit` rows. A full page is
    evidence the window was capped, and raises `LogicError` rather than walking past the
    rows that were left out; pass `allow_truncation=True` to accept the loss and keep
    going.
    """
    if start is None or end is None:
      raise ValueError(
        '`premium_index_price_kline_paged` walks a time window: pass both `start` and `end`'
      )
    lower = start
    upper = end
    width = upper - lower
    pages = 0
    while True:
      response = await self.premium_index_price_kline(
        category=category,
        symbol=symbol,
        interval=interval,
        start=lower,
        end=upper,
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
          f'`premium_index_price_kline_paged` requested the window {lower} to {upper} and the venue returned a full page of {len(rows)} rows, so it may hold more; advancing would move past the rows that were left out. Narrow the window, or pass `allow_truncation=True` to accept the loss.'
        )
      upper = lower - 1
      lower = upper - width
