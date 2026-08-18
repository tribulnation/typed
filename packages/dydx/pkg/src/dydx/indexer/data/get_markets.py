"""dYdX indexer get markets types and endpoint."""

from typing_extensions import TypedDict
from dataclasses import dataclass

from dydx.indexer.types import PerpetualMarket
from .core import IndexerMixin, response_parser

class GetMarketsResponse(TypedDict):
  """Endpoint mixin for markets_response."""
  markets: dict[str, PerpetualMarket]

parse_response = response_parser(GetMarketsResponse)

@dataclass
class GetMarkets(IndexerMixin):
  """Endpoint mixin for markets."""
  async def get_markets(
    self,
    *,
    market: str | None = None,
    limit: int | None = None,
    validate: bool | None = None
  ) -> GetMarketsResponse:
    """Fetch perpetual market metadata.
  
    Args:
      market: Specific market ticker to retrieve, for example `BTC-USD`.
      limit: Maximum number of market entries to return.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-perpetual-markets)
    """
    params: dict[str, object] = {}
    if market is not None:
      params['market'] = market
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', '/v4/perpetualMarkets', params=params)
    return parse_response(r, validate=self.validate(validate))

