"""dYdX indexer get megavault historical pnl types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing_extensions import Literal, TypedDict
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
class GetMegavaultHistoricalPnl(IndexerMixin):
  """Endpoint mixin for megavault_historical_pnl."""
  async def get_megavault_historical_pnl(
    self,
    *,
    resolution: Literal['hour', 'day'],
    validate: bool | None = None
  ) -> list[PnlTick]:
    """Get megavault historical pnl.
  
    Args:
      resolution: PnL tick resolution.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/vaults#get-megavault-historical-pnl)
    """
    params: dict[str, object] = {
      'resolution': resolution,
    }
    r = await self.request('GET', '/v4/vault/v1/megavault/historicalPnl', params=params)
    return parse_response(r, validate=self.validate(validate))

