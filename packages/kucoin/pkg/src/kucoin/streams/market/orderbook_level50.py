"""`/spotMarket/level2Depth50:{symbol}` — Subscribe to the 50 best ask/bid orders for one symbol -- pushed once every 100ms, only when the book changes within that depth."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class OrderbookLevel50update(TypedDict):
  """50-level ask/bid snapshot for a symbol -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  asks: list[tuple[str, str]]
  """Up to 50 best ask levels, each `[price, size]`, nearest first."""
  bids: list[tuple[str, str]]
  """Up to 50 best bid levels, each `[price, size]`, nearest first."""
  timestamp: int
  """Unix milliseconds of this update."""


_Type = OrderbookLevel50update
validate_update = validator[_Type](_Type)  # type: ignore


class OrderbookLevel50(StreamEndpoint):
  """Subscribe to `/spotMarket/level2Depth50:{symbol}` — mixed into `Market`, the product exposing `streams.spot_margin.orderbook_level50`."""

  def orderbook_level50(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[OrderbookLevel50update, Any, Any]:
    """Subscribe to the 50 best ask/bid orders for one symbol -- pushed once every 100ms, only when the book changes within that depth.

    Args:
      symbol: Trading pair symbol, for example `BTC-USDT`. The venue's own topic syntax accepts a comma-joined list of up to 100 symbols on one subscription; this spec models the single-symbol form.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/spotMarket/level2Depth50:{symbol}',
      validator=validate_update,
      validate=validate,
    )
