"""`spot.market_data.depth` -- public Spot market data."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class OrderBook(TypedDict):
  """One pair's L2 order book."""

  asks: NotRequired[list[tuple[str, str, int]]]
  """Ask side, best first."""
  bids: NotRequired[list[tuple[str, str, int]]]
  """Bid side, best first."""


validate_depth = validator(dict[str, OrderBook])


class Depth(RpcEndpoint):
  """`spot.market_data.depth`."""

  async def depth(
    self,
    *,
    pair: str,
    asset_version: Literal[1] | None = None,
    count: int | None = None,
    asset_class: Literal['tokenized_asset'] | None = None,
  ) -> dict[str, OrderBook]:
    """Returns level 2 (L2) order book, which describes the individual price levels in the book with aggregated order quantities at each level.

    Args:
      pair: Asset pair to get data for.
      asset_version: Controls whether response keys use Kraken's internal names or display names. Omitted (default): internal names are used. `assetVersion=1`: display names are used. Only `assetVersion=1` is currently supported.
      count: Maximum number of asks/bids.
      asset_class: This parameter is required on requests for non-crypto pairs, i.e. use `tokenized_asset` for xstocks.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/market-data/get-order-book)
    """
    params: dict = {
      'pair': pair,
    }
    if asset_version is not None:
      params['assetVersion'] = asset_version
    if count is not None:
      params['count'] = count
    if asset_class is not None:
      params['asset_class'] = asset_class

    return await self.request('/0/public/Depth', params, validator=validate_depth)
