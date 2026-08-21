"""dYdX indexer get parent asset positions types and endpoint."""

from dataclasses import dataclass
from decimal import Decimal
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
class GetParentAssetPositions(IndexerMixin):
  """Endpoint mixin for parent_asset_positions."""
  async def get_parent_asset_positions(
    self,
    address: str,
    *,
    parent_subaccount: int,
    validate: bool | None = None
  ) -> list[AssetPosition]:
    """Get parent asset positions.
  
    Args:
      address: Wallet address that owns the account.
      parent_subaccount: Parent subaccount number.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/accounts#get-parent-asset-positions)
    """
    params: dict[str, object] = {
      'address': address,
      'parentSubaccountNumber': parent_subaccount,
    }
    r = await self.request('GET', '/v4/assetPositions/parentSubaccountNumber', params=params)
    return parse_response(r, validate=self.validate(validate))
