"""dYdX indexer get trades types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing_extensions import Literal, TypedDict
from .core import IndexerMixin, response_parser

class Trade(TypedDict):
  """Trade payload."""
  id: str
  side: Literal['BUY', 'SELL']
  size: Decimal
  price: Decimal
  type: Literal['LIMIT', 'LIQUIDATED', 'DELEVERAGED']
  createdAt: datetime
  createdAtHeight: str

class TradesResponse(TypedDict):
  """TradesResponse payload."""
  trades: list[Trade]

parse_response = response_parser(TradesResponse)

@dataclass
class GetTrades(IndexerMixin):
  """Endpoint mixin for trades."""
  async def get_trades(
    self,
    market: str,
    *,
    starting_before_or_at_height: int | None = None,
    limit: int | None = None,
    validate: bool | None = None
  ) -> TradesResponse:
    """Get trades.
  
    Args:
      market: Perpetual market ticker.
      starting_before_or_at_height: Latest block height to include.
      limit: Maximum number of trades to return.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-trades)
    """
    params: dict[str, object] = {}
    if starting_before_or_at_height is not None:
      params['startingBeforeOrAtHeight'] = starting_before_or_at_height
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', f'/v4/trades/perpetualMarket/{market}', params=params)
    return parse_response(r, validate=self.validate(validate))

