"""dYdX indexer get subaccount types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing_extensions import Literal, NotRequired, TypedDict
from .core import IndexerMixin, response_parser

class AssetPosition(TypedDict):
  """AssetPosition payload."""
  size: Decimal
  symbol: str
  side: Literal['LONG', 'SHORT']
  assetId: str
  subaccountNumber: int

class PerpetualPosition(TypedDict):
  """PerpetualPosition payload."""
  market: str
  status: Literal['OPEN', 'CLOSED', 'LIQUIDATED']
  side: Literal['LONG', 'SHORT']
  size: Decimal
  maxSize: Decimal
  entryPrice: Decimal
  exitPrice: NotRequired[Decimal | None]
  realizedPnl: NotRequired[Decimal | None]
  unrealizedPnl: NotRequired[Decimal | None]
  createdAt: datetime
  createdAtHeight: str
  closedAt: NotRequired[datetime | None]
  sumOpen: Decimal
  sumClose: Decimal
  netFunding: Decimal
  subaccountNumber: int

AssetPositionsMap = dict[str, AssetPosition]

PerpetualPositionsMap = dict[str, PerpetualPosition]

class Subaccount(TypedDict):
  """Subaccount payload."""
  address: str
  subaccountNumber: int
  equity: Decimal
  freeCollateral: Decimal
  openPerpetualPositions: PerpetualPositionsMap
  assetPositions: AssetPositionsMap
  marginEnabled: bool
  updatedAtHeight: str
  latestProcessedBlockHeight: str

class GetSubaccountResponse(TypedDict):
  """Endpoint mixin for subaccount_response."""
  subaccount: Subaccount

parse_response = response_parser(GetSubaccountResponse)

@dataclass
class GetSubaccount(IndexerMixin):
  """Endpoint mixin for subaccount."""
  async def get_subaccount(
    self,
    address: str,
    subaccount: int,
    validate: bool | None = None
  ) -> GetSubaccountResponse:
    """Get subaccount.
  
    Args:
      address: Account address.
      subaccount: Subaccount number.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-subaccount)
    """
    r = await self.request('GET', f'/v4/addresses/{address}/subaccountNumber/{subaccount}')
    return parse_response(r, validate=self.validate(validate))
