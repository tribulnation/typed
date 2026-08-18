from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import AsyncIterator, Literal, TypedDict
from typed_core.exceptions import LogicError
from coinbase.core.endpoint.rpc import RpcEndpoint


class Candle(TypedDict):
  """One OHLCV candle bucket."""

  start: str
  """UNIX timestamp marking the start of the candle interval."""
  low: str
  """Lowest price during the interval."""
  high: str
  """Highest price during the interval."""
  open: str
  """Opening (first-trade) price during the interval."""
  close: str
  """Closing (last-trade) price during the interval."""
  volume: str
  """Trading volume during the interval."""


class CandlesResponse(TypedDict):
  """A window of OHLCV candles."""

  candles: list[Candle]
  """Candles, newest first."""


@dataclass(frozen=True, kw_only=True)
class Candles(RpcEndpoint):
  """`GET /api/v3/brokerage/products/{product_id}/candles`."""

  async def __call__(
    self,
    product_id: str,
    *,
    start: int,
    end: int,
    granularity: Literal[
      'UNKNOWN_GRANULARITY',
      'ONE_MINUTE',
      'FIVE_MINUTE',
      'FIFTEEN_MINUTE',
      'THIRTY_MINUTE',
      'ONE_HOUR',
      'TWO_HOUR',
      'FOUR_HOUR',
      'SIX_HOUR',
      'ONE_DAY',
    ],
    limit: int | None = None,
  ) -> CandlesResponse:
    """Get historical OHLCV candles for one product.

    Args:
      product_id: The trading pair, e.g. `BTC-USD`.
      start: UNIX timestamp for the start of the requested window.
      end: UNIX timestamp for the end of the requested window.
      granularity: The candle interval width.
      limit: Number of candle buckets to return. Default 350, maximum 350.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/products/get-product-candles)
    """
    params: dict = {
      'start': start,
      'end': end,
      'granularity': granularity,
    }
    if limit is not None:
      params['limit'] = limit
    return await self.authed_request(
      'GET',
      f'/api/v3/brokerage/products/{product_id}/candles',
      params=params,
      validator=validator(CandlesResponse),
    )

  async def paged(
    self,
    product_id: str,
    *,
    start: int,
    end: int,
    granularity: Literal[
      'UNKNOWN_GRANULARITY',
      'ONE_MINUTE',
      'FIVE_MINUTE',
      'FIFTEEN_MINUTE',
      'THIRTY_MINUTE',
      'ONE_HOUR',
      'TWO_HOUR',
      'FOUR_HOUR',
      'SIX_HOUR',
      'ONE_DAY',
    ],
    limit: int | None = None,
    max_pages: int | None = None,
    allow_truncation: bool = False,
  ) -> AsyncIterator[CandlesResponse]:
    """Yield successive pages of this endpoint.

    Moves the `start`–`end` window backwards by its own width and stops on the first
    empty window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `start` and `end` state, so choose a
    window the venue answers in one response — at most `limit` rows. A full page is
    evidence the window was capped, and raises `LogicError` rather than walking past the
    rows that were left out; pass `allow_truncation=True` to accept the loss and keep
    going.
    """
    lower = start
    upper = end
    width = upper - lower
    pages = 0
    while True:
      response = await self.__call__(
        product_id, start=lower, end=upper, granularity=granularity, limit=limit
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('candles') if response is not None else None
      if not rows:
        break
      if not allow_truncation and len(rows) >= (limit if limit is not None else 350):
        raise LogicError(
          f'`paged` requested the window {lower} to {upper} and the venue returned a full page of {len(rows)} rows, so it may hold more; advancing would move past the rows that were left out. Narrow the window, or pass `allow_truncation=True` to accept the loss.'
        )
      upper = lower - 1
      lower = upper - width
