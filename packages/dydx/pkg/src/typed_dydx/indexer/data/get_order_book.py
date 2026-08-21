"""dYdX indexer get order book types and endpoint."""

from dataclasses import dataclass
from decimal import Decimal
from typing_extensions import TypedDict
from .core import IndexerMixin, response_parser

class BookEntry(TypedDict):
  """BookEntry payload."""
  price: Decimal
  size: Decimal

class OrderBook(TypedDict):
  """OrderBook payload."""
  bids: list[BookEntry]
  asks: list[BookEntry]

parse_response = response_parser(OrderBook)

@dataclass
class GetOrderBook(IndexerMixin):
  """Endpoint mixin for order_book."""
  async def get_order_book(
    self,
    market: str,
    validate: bool | None = None
  ) -> OrderBook:
    """Get order book.
  
    Args:
      market: Perpetual market ticker.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-perpetual-market-orderbook)
    """
    r = await self.request('GET', f'/v4/orderbooks/perpetualMarket/{market}')
    return parse_response(r, validate=self.validate(validate))

