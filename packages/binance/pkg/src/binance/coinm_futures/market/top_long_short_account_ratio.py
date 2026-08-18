from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMTopTraderLongShortAccountRatio(TypedDict):
  """Top-trader long/short account ratio for one period bucket."""

  pair: str
  """Underlying pair."""
  longShortRatio: str
  """Long/short ratio."""
  longAccount: str
  """Proportion of top-trader accounts net long, as a decimal fraction (e.g. "0.6971", not a percent string)."""
  shortAccount: str
  """Proportion of top-trader accounts net short, as a decimal fraction (e.g. "0.2929", not a percent string)."""
  timestamp: int
  """End time of the period, in milliseconds since epoch."""


class TopLongShortAccountRatio(RpcEndpoint):
  """The proportion of net long and net short accounts to total accounts, among the top 20% of users by margin balance. Each account is counted once. Long Account % = accounts of top traders net long / total accounts of top traders with open positions; Short Account % is the net-short equivalent; Long/Short Ratio (Accounts) = Long Account % / Short Account %."""

  async def top_long_short_account_ratio(
    self,
    *,
    pair: str,
    period: Literal['5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d'],
    limit: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    validate: bool | None = None,
  ) -> list[CoinMTopTraderLongShortAccountRatio]:
    """The proportion of net long and net short accounts to total accounts, among the top 20% of users by margin balance. Each account is counted once. Long Account % = accounts of top traders net long / total accounts of top traders with open positions; Short Account % is the net-short equivalent; Long/Short Ratio (Accounts) = Long Account % / Short Account %.

    Args:
      pair: Underlying pair.
      period: Bucket period.
      limit: Number of records to return.
      start_time: Start time, in milliseconds since epoch.
      end_time: End time, in milliseconds since epoch.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#top-trader-long-short-ratio-accounts)
    """
    params: dict = {
      'pair': pair,
      'period': period,
    }
    if limit is not None:
      params['limit'] = limit
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    _Response = list[CoinMTopTraderLongShortAccountRatio]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/futures/data/topLongShortAccountRatio',
      params=params,
      validator=_validator,
      validate=validate,
    )
