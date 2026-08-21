"""dYdX indexer get rewards types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from .. import timestamp as ts
from typing_extensions import TypedDict
from .core import IndexerMixin, response_parser

class HistoricalBlockTradingReward(TypedDict):
  """HistoricalBlockTradingReward payload."""
  tradingReward: Decimal
  createdAtHeight: str
  createdAt: datetime

parse_response = response_parser(list[HistoricalBlockTradingReward])

@dataclass
class GetRewards(IndexerMixin):
  """Endpoint mixin for rewards."""
  async def get_rewards(
    self,
    address: str,
    *,
    limit: int | None = None,
    starting_before_or_at_height: int | None = None,
    starting_before_or_at: datetime | None = None,
    validate: bool | None = None
  ) -> list[HistoricalBlockTradingReward]:
    """Get rewards.
  
    Args:
      address: Wallet address that owns the account.
      limit: Maximum number of results to return.
      starting_before_or_at_height: Only include rewards starting at or before this block height.
      starting_before_or_at: Only include rewards starting at or before this timestamp.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-rewards)
    """
    params: dict[str, object] = {}
    if limit is not None:
      params['limit'] = limit
    if starting_before_or_at_height is not None:
      params['startingBeforeOrAtHeight'] = starting_before_or_at_height
    if starting_before_or_at is not None:
      params['startingBeforeOrAt'] = ts.dump(starting_before_or_at)
    r = await self.request('GET', f'/v4/historicalBlockTradingRewards/{address}', params=params)
    return parse_response(r, validate=self.validate(validate))
