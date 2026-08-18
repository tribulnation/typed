"""dYdX indexer get vaults historical pnl types and endpoint."""

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

class VaultHistoricalPnl(TypedDict):
  """Vault historical PnL payload."""
  ticker: str
  historicalPnl: PnlTick

parse_response = response_parser(list[VaultHistoricalPnl])

@dataclass
class GetVaultsHistoricalPnl(IndexerMixin):
  """Endpoint mixin for vaults_historical_pnl."""
  async def get_vaults_historical_pnl(
    self,
    *,
    resolution: Literal['hour', 'day'],
    validate: bool | None = None
  ) -> list[VaultHistoricalPnl]:
    """Get vaults historical pnl.
  
    Args:
      resolution: PnL tick resolution.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http/vaults#get-vaults-historical-pnl)
    """
    params: dict[str, object] = {
      'resolution': resolution,
    }
    r = await self.request('GET', '/v4/vault/v1/vaults/historicalPnl', params=params)
    return parse_response(r, validate=self.validate(validate))

