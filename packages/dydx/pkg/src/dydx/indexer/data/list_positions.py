"""dYdX indexer list positions types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from .. import timestamp as ts
from typing_extensions import Literal, NotRequired, TypedDict
from .core import IndexerMixin, response_parser

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

class PositionsResponse(TypedDict):
  """PositionsResponse payload."""
  positions: list[PerpetualPosition]

parse_response = response_parser(PositionsResponse)

@dataclass
class ListPositions(IndexerMixin):
  """Endpoint mixin for ListPositions."""
  async def list_positions(
    self, address: str, *,
    subaccount: int,
    status: Literal['OPEN', 'CLOSED', 'LIQUIDATED'] | None = None,
    limit: int | None = None,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    validate: bool | None = None
  ) -> PositionsResponse:
    """List positions.
  
    Args:
      address: Wallet address that owns the subaccount.
      subaccount: Subaccount number.
      status: Position status filter.
      limit: Maximum number of positions to return.
      created_before_or_at_height: Latest block height to include.
      created_before_or_at: Latest timestamp to include.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#list-positions)
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
    r = await self.request('GET', '/v4/perpetualPositions', params=params)
    return parse_response(r, validate=self.validate(validate))

