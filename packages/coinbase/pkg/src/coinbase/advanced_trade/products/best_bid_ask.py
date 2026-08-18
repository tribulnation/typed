from dataclasses import dataclass
from datetime import datetime
from typed_core.validation import validator
from typing_extensions import NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class L2levelAsksItem(TypedDict):
  """One order book price level."""

  price: str
  """Price at this level."""
  size: str
  """Aggregate size available at this level."""


class L2levelBidsItem(TypedDict):
  """One order book price level."""

  price: str
  """Price at this level."""
  size: str
  """Aggregate size available at this level."""


class PriceBook(TypedDict):
  """One product's order book snapshot."""

  product_id: str
  """The trading pair, e.g. `BTC-USD`."""
  bids: list[L2levelBidsItem]
  """Bid levels, best first."""
  asks: list[L2levelAsksItem]
  """Ask levels, best first."""
  time: NotRequired[datetime]
  """Time the book snapshot was taken."""


class BestBidAskResponse(TypedDict):
  """Best-bid/ask snapshots for the requested products."""

  pricebooks: list[PriceBook]
  """One top-of-book snapshot per product."""


@dataclass(frozen=True, kw_only=True)
class BestBidAsk(RpcEndpoint):
  """`GET /api/v3/brokerage/best_bid_ask`."""

  async def __call__(
    self, *, product_ids: list[str] | None = None
  ) -> BestBidAskResponse:
    """Get the best bid/ask price and size for one or more products.

    Args:
      product_ids: Trading pairs to fetch, e.g. `BTC-USD`. Omit to get every product.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/products/get-best-bid-ask)
    """
    params = {}
    if product_ids is not None:
      params['product_ids'] = product_ids
    return await self.authed_request(
      'GET',
      '/api/v3/brokerage/best_bid_ask',
      params=params,
      validator=validator(BestBidAskResponse),
    )
