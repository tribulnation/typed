"""dYdX indexer get candles types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from .. import timestamp as ts
from typing_extensions import AsyncIterable, Literal, NotRequired, Sequence, TypedDict
from .core import IndexerMixin, response_parser

class Candle(TypedDict):
  """Candle payload."""
  startedAt: datetime
  ticker: str
  resolution: Literal['1MIN', '5MINS', '15MINS', '30MINS', '1HOUR', '4HOURS', '1DAY']
  low: Decimal
  high: Decimal
  open: Decimal
  close: Decimal
  baseTokenVolume: Decimal
  usdVolume: Decimal
  trades: int
  startingOpenInterest: Decimal
  orderbookMidPriceOpen: NotRequired[Decimal | None]
  orderbookMidPriceClose: NotRequired[Decimal | None]

class CandlesResponse(TypedDict):
  """Candles response payload."""
  candles: list[Candle]

parse_response = response_parser(CandlesResponse)

@dataclass
class GetCandles(IndexerMixin):
  """Endpoint mixin for candles."""
  async def get_candles(
    self,
    market: str,
    *,
    resolution: Literal[
      '1MIN', '5MINS', '15MINS', '30MINS', '1HOUR', '4HOURS', '1DAY'
    ],
    from_iso: datetime | None = None,
    to_iso: datetime | None = None,
    limit: int | None = None,
    validate: bool | None = None
  ) -> CandlesResponse:
    """Fetch candles for a perpetual market.
  
    Args:
      market: Perpetual market ticker.
      resolution: Candle resolution.
      from_iso: Start timestamp in ISO 8601 format.
      to_iso: End timestamp in ISO 8601 format.
      limit: Maximum number of candles to return.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-candles)
    """
    params: dict[str, object] = {
      'resolution': resolution,
    }
    if from_iso is not None:
      params['fromISO'] = ts.dump(from_iso)
    if to_iso is not None:
      params['toISO'] = ts.dump(to_iso)
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', f'/v4/candles/perpetualMarkets/{market}', params=params)
    return parse_response(r, validate=self.validate(validate))

Resolution = Literal['1MIN', '5MINS', '15MINS', '30MINS', '1HOUR', '4HOURS', '1DAY']

@dataclass
class GetCandlesPaged(GetCandles):
  """Endpoint mixin for candles_paged."""
  async def get_candles_paged(
    self,
    market: str,
    resolution: Resolution,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = None,
  ) -> AsyncIterable[Sequence[Candle]]:
    """Page through candles for a perpetual market.
  
    Args:
      market: The market ticker (e.g. `'BTC-USD'`).
      resolution: The resolution of the candles.
      start: If given, fetches candles starting from the given timestamp.
      end: If given, fetches candles up to and including the given timestamp.
      limit: The max. number of candles to retrieve per request (default: 1000, max: 1000).
  
    Returns:
      An async iterable of candle pages. Each request advances by the last candle timestamp until an empty page is returned.
    """
    last_time = end
    while True:
      response = await self.get_candles(
        market,
        resolution=resolution,
        from_iso=start,
        to_iso=last_time,
        limit=limit,
      )
      candles = response['candles']
      if not candles:
        break
      yield candles
      last_time = candles[-1]['startedAt']
