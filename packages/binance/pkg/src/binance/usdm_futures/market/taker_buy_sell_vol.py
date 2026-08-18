from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class TakerBuySellVolume(TypedDict):
  """Taker buy/sell volume at one period bucket."""

  buySellRatio: str
  """Ratio of taker buy volume to taker sell volume."""
  buyVol: str
  """Taker buy volume during the bucket."""
  sellVol: str
  """Taker sell volume during the bucket."""
  timestamp: int
  """Period start time, in milliseconds since epoch."""


class TakerBuySellVol(RpcEndpoint):
  """Taker buy/sell volume ratio for a symbol, bucketed by period."""

  async def taker_buy_sell_vol(
    self,
    *,
    symbol: str,
    period: Literal['5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d'],
    limit: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    validate: bool | None = None,
  ) -> list[TakerBuySellVolume]:
    """Taker buy/sell volume ratio for a symbol, bucketed by period.

    Args:
      symbol: Trading symbol, e.g. BTCUSDT.
      period: Bucket width for each returned data point.
      limit: Number of data points to return.
      start_time: Start time, in milliseconds since epoch.
      end_time: End time, in milliseconds since epoch.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#taker-buy-sell-volume)
    """
    params: dict = {
      'symbol': symbol,
      'period': period,
    }
    if limit is not None:
      params['limit'] = limit
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    _Response = list[TakerBuySellVolume]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/futures/data/takerlongshortRatio',
      params=params,
      validator=_validator,
      validate=validate,
    )
