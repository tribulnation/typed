"""`/callauction/level2Depth50:{symbol}` — Subscribe to the 50 best ask/bid orders of a symbol's call-auction order book -- only pushes while that symbol is in its pre-market call-auction phase (a new-listing mechanism; see `spot.market.call_auction_info`/`call_auction_part_orderbook` REST siblings for the same concept). Data only pushes when the call-auction book changes."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class CallAuctionOrderbookLevel50update(TypedDict):
  """50-level call-auction ask/bid snapshot for a symbol -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section). Same shape as the regular `OrderbookLevel50Update`."""

  asks: list[tuple[str, str]]
  """Up to 50 best call-auction ask levels, each `[price, size]`, nearest first."""
  bids: list[tuple[str, str]]
  """Up to 50 best call-auction bid levels, each `[price, size]`, nearest first."""
  timestamp: int
  """Unix milliseconds of this update."""


_Type = CallAuctionOrderbookLevel50update
validate_update = validator[_Type](_Type)  # type: ignore


class CallAuctionOrderbookLevel50(StreamEndpoint):
  """Subscribe to `/callauction/level2Depth50:{symbol}` — mixed into `Market`, the product exposing `streams.spot_margin.call_auction_orderbook_level50`."""

  def call_auction_orderbook_level50(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[CallAuctionOrderbookLevel50update, Any, Any]:
    """Subscribe to the 50 best ask/bid orders of a symbol's call-auction order book -- only pushes while that symbol is in its pre-market call-auction phase (a new-listing mechanism; see `spot.market.call_auction_info`/`call_auction_part_orderbook` REST siblings for the same concept). Data only pushes when the call-auction book changes.

    Args:
      symbol: Trading pair symbol, for example `BTC-USDT`. Unlike the regular Level1/5/50 topics, the docs page's own example shows a single symbol per subscription and does not advertise multi-symbol support.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/callauction/level2Depth50:{symbol}',
      validator=validate_update,
      validate=validate,
    )
