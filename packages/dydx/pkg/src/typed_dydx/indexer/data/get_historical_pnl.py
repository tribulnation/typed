"""dYdX indexer get historical pnl types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from .. import timestamp as ts
from typing_extensions import TypedDict
from .core import IndexerMixin, response_parser

class PnlTick(TypedDict):
  """PnL tick payload."""
  blockHeight: str
  blockTime: datetime
  createdAt: datetime
  equity: Decimal
  totalPnl: Decimal
  netTransfer: Decimal

parse_response = response_parser(list[PnlTick])

@dataclass
class GetHistoricalPnl(IndexerMixin):
  """Endpoint mixin for historical_pnl."""
  async def get_historical_pnl(
    self,
    address: str,
    *,
    subaccount: int,
    limit: int | None = None,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    created_on_or_after_height: int | None = None,
    created_on_or_after: datetime | None = None,
    page: int | None = None,
    validate: bool | None = None
  ) -> list[PnlTick]:
    """Get historical pnl.
  
    Args:
      address: Wallet address that owns the account.
      subaccount: Subaccount number.
      limit: Maximum number of results to return.
      created_before_or_at_height: Restrict results to entries created at or before a specific block height.
      created_before_or_at: Restrict results to entries created at or before a specific timestamp.
      created_on_or_after_height: Restrict results to entries created on or after a specific block height.
      created_on_or_after: Restrict results to entries created on or after a specific timestamp.
      page: Page number for paginated results.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-historical-pnl)
    """
    params: dict[str, object] = {
      'address': address,
      'subaccountNumber': subaccount,
    }
    if limit is not None:
      params['limit'] = limit
    if created_before_or_at_height is not None:
      params['createdBeforeOrAtHeight'] = created_before_or_at_height
    if created_before_or_at is not None:
      params['createdBeforeOrAt'] = ts.dump(created_before_or_at)
    if created_on_or_after_height is not None:
      params['createdOnOrAfterHeight'] = created_on_or_after_height
    if created_on_or_after is not None:
      params['createdOnOrAfter'] = ts.dump(created_on_or_after)
    if page is not None:
      params['page'] = page
    r = await self.request('GET', '/v4/historical-pnl', params=params)
    return parse_response(r, validate=self.validate(validate))
