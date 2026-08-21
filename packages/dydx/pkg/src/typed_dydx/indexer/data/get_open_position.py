"""dYdX indexer get open position types and endpoint."""

from dataclasses import dataclass

from .list_positions import ListPositions, PerpetualPosition


@dataclass
class GetOpenPosition(ListPositions):
  """Endpoint mixin for open_position."""
  async def get_open_position(
    self,
    address: str,
    market: str,
    *,
    subaccount: int,
    validate: bool | None = None,
  ) -> PerpetualPosition | None:
    """Fetch one open perpetual position for a subaccount.
  
    Args:
      address: Wallet address.
      market: Market ticker.
      subaccount: Subaccount number.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
    """
    response = await self.list_positions(
      address,
      subaccount=subaccount,
      status='OPEN',
      validate=validate,
    )
    positions = response['positions']
    for position in positions:
      if position['market'] == market:
        return position
    return None
