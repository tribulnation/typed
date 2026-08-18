from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class TopTraderAccountRatio(TypedDict):
  """Top traders' long/short account ratio at one period bucket."""

  symbol: str
  """Trading symbol."""
  longShortRatio: str
  """Ratio of long to short accounts among top traders."""
  longAccount: str
  """Proportion of top-trader accounts holding long positions."""
  shortAccount: str
  """Proportion of top-trader accounts holding short positions."""
  timestamp: int
  """Period end time, in milliseconds since epoch."""


class TopLongShortAccountRatio(RpcEndpoint):
  """Long/short account ratio of the top traders (by account count) for a symbol, bucketed by period."""

  async def top_long_short_account_ratio(
    self,
    *,
    symbol: str,
    period: Literal['5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d'],
    limit: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    validate: bool | None = None,
  ) -> list[TopTraderAccountRatio]:
    """Long/short account ratio of the top traders (by account count) for a symbol, bucketed by period.

    Args:
      symbol: Trading symbol, e.g. BTCUSDT.
      period: Bucket width for each returned data point.
      limit: Number of data points to return.
      start_time: Start time, in milliseconds since epoch.
      end_time: End time, in milliseconds since epoch.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#top-trader-long-short-ratio-accounts)
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
    _Response = list[TopTraderAccountRatio]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/futures/data/topLongShortAccountRatio',
      params=params,
      validator=_validator,
      validate=validate,
    )
