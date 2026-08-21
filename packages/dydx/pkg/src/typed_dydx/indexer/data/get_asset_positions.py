"""dYdX indexer get asset positions types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from .. import timestamp as ts
from typing_extensions import Literal, TypedDict
from .core import IndexerMixin, response_parser

class AssetPosition(TypedDict):
  """AssetPosition payload."""
  size: Decimal
  symbol: str
  side: Literal['LONG', 'SHORT']
  assetId: str
  subaccountNumber: int

parse_response = response_parser(list[AssetPosition])

@dataclass
class GetAssetPositions(IndexerMixin):
  """Endpoint mixin for asset_positions."""
  async def get_asset_positions(
    self,
    address: str,
    *,
    subaccount: int,
    status: Literal['OPEN', 'CLOSED', 'LIQUIDATED'] | None = None,
    limit: int | None = None,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    validate: bool | None = None
  ) -> list[AssetPosition]:
    """Get asset positions.
  
    Args:
      address: Wallet address that owns the account.
      subaccount: Subaccount number.
      status: Position status filter.
      limit: Maximum number of results to return.
      created_before_or_at_height: Restrict results to entries created at or before a specific block height.
      created_before_or_at: Restrict results to entries created at or before a specific timestamp.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-asset-positions)
    """
    params: dict[str, object] = {
      'address': address,
      'subaccountNumber': subaccount,
    }
    if status is not None:
      params['status'] = status
    if limit is not None:
      params['limit'] = limit
    if created_before_or_at_height is not None:
      params['createdBeforeOrAtHeight'] = created_before_or_at_height
    if created_before_or_at is not None:
      params['createdBeforeOrAt'] = ts.dump(created_before_or_at)
    r = await self.request('GET', '/v4/assetPositions', params=params)
    return parse_response(r, validate=self.validate(validate))
