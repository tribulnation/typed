"""`GET /api/v1/market/orderbook/callauction/level2_{size}` — Get Call Auction Part OrderBook."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class CallAuctionPartOrderBook(TypedDict):
  """Call-auction order book depth, up to `size` levels per side."""

  time: int
  """Snapshot timestamp, Unix ms."""
  sequence: str
  """Order book sequence number, or `-1` when the symbol has no active call auction."""
  bids: list[tuple[str, str]]
  """Buy side, best price first. Empty outside a call-auction phase."""
  asks: list[tuple[str, str]]
  """Sell side, best price first. Empty outside a call-auction phase."""


_Type = CallAuctionPartOrderBook
adapter = validator[_Type](_Type)  # type: ignore


class CallAuctionPartOrderbook(RpcEndpoint):
  """`Get Call Auction Part OrderBook` — mixed into `Spot`, the product exposing `spot.call_auction_part_orderbook`."""

  async def call_auction_part_orderbook(
    self,
    size: Literal['20', '100'],
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> CallAuctionPartOrderBook:
    """Get order book depth for a symbol's call-auction opening phase, aggregated by price, limited to the requested number of price levels per side.

    Args:
      size: Number of price levels per side to return.
      symbol: Trading pair symbol, e.g. `BTC-USDT`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.request(
      'GET',
      f'/api/v1/market/orderbook/callauction/level2_{size}',
      params=params,
      validator=adapter,
      validate=validate,
    )
