"""`/callauction/callauctionData:{symbol}` — Subscribe to call-auction info for one symbol -- estimated clearing price/size and the current buy/sell order price ranges. Only pushes while the symbol is in its pre-market call-auction phase; see `spot.market.call_auction_info` for the REST equivalent."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class CallAuctionInfoUpdate(TypedDict):
  """One call-auction info snapshot for a symbol -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  symbol: str
  """Trading pair symbol."""
  estimatedPrice: str
  """Estimated call-auction clearing price."""
  estimatedSize: str
  """Estimated call-auction clearing size."""
  sellOrderRangeLowPrice: str
  """Lowest resting sell-order price."""
  sellOrderRangeHighPrice: str
  """Highest resting sell-order price."""
  buyOrderRangeLowPrice: str
  """Lowest resting buy-order price."""
  buyOrderRangeHighPrice: str
  """Highest resting buy-order price."""
  time: int
  """Unix milliseconds of this update."""


_Type = CallAuctionInfoUpdate
validate_update = validator[_Type](_Type)  # type: ignore


class CallAuctionInfo(StreamEndpoint):
  """Subscribe to `/callauction/callauctionData:{symbol}` — mixed into `Market`, the product exposing `streams.spot_margin.call_auction_info`."""

  def call_auction_info(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[CallAuctionInfoUpdate, Any, Any]:
    """Subscribe to call-auction info for one symbol -- estimated clearing price/size and the current buy/sell order price ranges. Only pushes while the symbol is in its pre-market call-auction phase; see `spot.market.call_auction_info` for the REST equivalent.

    Args:
      symbol: Trading pair symbol, for example `BTC-USDT`.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/callauction/callauctionData:{symbol}',
      validator=validate_update,
      validate=validate,
    )
