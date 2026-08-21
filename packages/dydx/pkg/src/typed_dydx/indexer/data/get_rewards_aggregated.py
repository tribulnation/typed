"""dYdX indexer get rewards aggregated types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from .. import timestamp as ts
from typing_extensions import Literal, TypedDict
from .core import IndexerMixin, response_parser

class HistoricalTradingRewardAggregation(TypedDict):
  """HistoricalTradingRewardAggregation payload."""
  tradingReward: Decimal
  startedAtHeight: str
  startedAt: datetime
  endedAtHeight: str
  endedAt: datetime

parse_response = response_parser(list[HistoricalTradingRewardAggregation])

@dataclass
class GetRewardsAggregated(IndexerMixin):
  """Endpoint mixin for rewards_aggregated."""
  async def get_rewards_aggregated(
    self,
    address: str,
    *,
    period: Literal['DAILY', 'WEEKLY', 'MONTHLY'],
    limit: int | None = None,
    starting_before_or_at: datetime | None = None,
    starting_before_or_at_height: int | None = None,
    validate: bool | None = None
  ) -> list[HistoricalTradingRewardAggregation]:
    """Get rewards aggregated.
  
    Args:
      address: Wallet address that owns the account.
      period: Aggregation period.
      limit: Maximum number of results to return.
      starting_before_or_at: Only include aggregations starting at or before this timestamp.
      starting_before_or_at_height: Only include aggregations starting at or before this block height.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-rewards-aggregated)
    """
    params: dict[str, object] = {
      'period': period,
    }
    if limit is not None:
      params['limit'] = limit
    if starting_before_or_at is not None:
      params['startingBeforeOrAt'] = ts.dump(starting_before_or_at)
    if starting_before_or_at_height is not None:
      params['startingBeforeOrAtHeight'] = starting_before_or_at_height
    r = await self.request('GET', f'/v4/historicalTradingRewardAggregations/{address}', params=params)
    return parse_response(r, validate=self.validate(validate))
