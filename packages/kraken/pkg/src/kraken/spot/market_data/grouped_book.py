"""`spot.market_data.grouped_book` -- public Spot market data."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class GroupedPriceLevelAsksItem(TypedDict):
  """One grouped price level."""

  price: NotRequired[str]
  """Grouped price level."""
  qty: NotRequired[str]
  """Aggregated quantity at this price level."""


class GroupedPriceLevelBidsItem(TypedDict):
  """One grouped price level."""

  price: NotRequired[str]
  """Grouped price level."""
  qty: NotRequired[str]
  """Aggregated quantity at this price level."""


class GroupedOrderBook(TypedDict):
  """One pair's grouped order book."""

  pair: NotRequired[str]
  """Asset pair."""
  grouping: NotRequired[int]
  """The grouping value used."""
  bids: NotRequired[list[GroupedPriceLevelBidsItem]]
  """Aggregated bid levels."""
  asks: NotRequired[list[GroupedPriceLevelAsksItem]]
  """Aggregated ask levels."""


validate_grouped_book = validator(GroupedOrderBook)


class GroupedBook(RpcEndpoint):
  """`spot.market_data.grouped_book`."""

  async def grouped_book(
    self,
    *,
    pair: str,
    depth: Literal[10, 25, 100, 250, 1000] | None = None,
    grouping: Literal[1, 5, 10, 25, 50, 100, 250, 500, 1000] | None = None,
  ) -> GroupedOrderBook:
    """Aggregates the volume in the order book over a specified tick range, for a summary of liquidity deep into the book (useful for UI display). Bids and asks between grouped price levels are accumulated to the nearest passive level (asks rounded up, bids down).

    Args:
      pair: Asset pair to get order book for.
      depth: The number of price levels to return per side (bids/asks).
      grouping: How many tick levels should be within each price level. Bids and asks between grouped price levels are accumulated to the nearest passive level (asks rounded up, bids down).

    References:
      - [Official docs](https://docs.kraken.com/api-reference/market-data/get-grouped-order-book)
    """
    params: dict = {
      'pair': pair,
    }
    if depth is not None:
      params['depth'] = depth
    if grouping is not None:
      params['grouping'] = grouping

    return await self.request(
      '/0/public/GroupedBook', params, validator=validate_grouped_book
    )
