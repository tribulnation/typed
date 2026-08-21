"""dYdX indexer get market types and endpoint."""

from dataclasses import dataclass

from typed_dydx.indexer.types.market import PerpetualMarket

from .get_markets import GetMarkets


@dataclass
class GetMarket(GetMarkets):
  """Endpoint mixin for market."""
  async def get_market(
    self,
    market: str,
    *,
    validate: bool | None = None,
  ) -> PerpetualMarket:
    """Fetch one perpetual market by ticker.
  
    Args:
      market: Market ticker.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
    """
    response = await self.get_markets(market=market, limit=1, validate=validate)
    return response['markets'][market] if 'markets' in response else response[market]
