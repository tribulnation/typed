"""dYdX indexer get parent fills types and endpoint."""

from typing_extensions import Literal, NotRequired, TypedDict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from .. import timestamp as ts
from .core import IndexerMixin, response_parser

class Fill(TypedDict):
  """Fill payload."""
  id: str
  side: Literal['BUY', 'SELL']
  liquidity: Literal['MAKER', 'TAKER']
  type: Literal['LIMIT', 'LIQUIDATED', 'LIQUIDATION', 'DELEVERAGED', 'OFFSETTING']
  market: str
  marketType: Literal['PERPETUAL', 'SPOT']
  price: Decimal
  size: Decimal
  fee: Decimal
  affiliateRevShare: Decimal
  createdAt: datetime
  createdAtHeight: str
  orderId: NotRequired[str | None]
  clientMetadata: NotRequired[str | None]
  subaccountNumber: int
  builderFee: NotRequired[Decimal | None]
  builderAddress: NotRequired[str | None]
  positionSizeBefore: NotRequired[Decimal | None]
  entryPriceBefore: NotRequired[Decimal | None]
  positionSideBefore: NotRequired[Literal['LONG', 'SHORT'] | None]

class FillsResponse(TypedDict):
  """Fills response payload."""
  fills: list[Fill]

parse_response = response_parser(FillsResponse)

@dataclass
class GetParentFills(IndexerMixin):
  """Endpoint mixin for parent_fills."""
  async def get_parent_fills(
    self,
    address: str,
    *,
    parent_subaccount: int,
    limit: int | None = None,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    market: str | None = None,
    market_type: Literal['PERPETUAL', 'SPOT'] | None = None,
    validate: bool | None = None
  ) -> FillsResponse:
    """Get parent fills.
  
    Args:
      address: Wallet address that owns the account.
      parent_subaccount: Parent subaccount number.
      limit: Maximum number of results to return.
      created_before_or_at_height: Restrict results to entries created at or before a specific block height.
      created_before_or_at: Latest timestamp to include.
      market: Ticker filter.
      market_type: Market type filter.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-parent-fills)
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
    if market is not None:
      params['market'] = market
    if market_type is not None:
      params['marketType'] = market_type
    r = await self.request('GET', '/v4/fills/parentSubaccountNumber', params=params)
    return parse_response(r, validate=self.validate(validate))
