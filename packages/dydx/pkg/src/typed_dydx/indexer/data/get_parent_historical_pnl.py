"""dYdX indexer get parent historical pnl types and endpoint."""

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
class GetParentHistoricalPnl(IndexerMixin):
  """Endpoint mixin for parent_historical_pnl."""
  async def get_parent_historical_pnl(
    self,
    address: str,
    *,
    parent_subaccount: int,
    limit: int | None = None,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    created_on_or_after_height: int | None = None,
    created_on_or_after: datetime | None = None,
    validate: bool | None = None
  ) -> list[PnlTick]:
    """Get parent historical pnl.
  
    Args:
      address: Wallet address that owns the account.
      parent_subaccount: Parent subaccount number.
      limit: Maximum number of results to return.
      created_before_or_at_height: Restrict results to entries created at or before a specific block height.
      created_before_or_at: Restrict results to entries created at or before a specific timestamp.
      created_on_or_after_height: Restrict results to entries created on or after a specific block height.
      created_on_or_after: Restrict results to entries created on or after a specific timestamp.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-parent-historical-pnl)
    """
    params: dict[str, object] = {
      'address': address,
      'parentSubaccountNumber': parent_subaccount,
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
    r = await self.request('GET', '/v4/historical-pnl/parentSubaccountNumber', params=params)
    return parse_response(r, validate=self.validate(validate))
