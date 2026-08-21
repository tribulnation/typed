"""`/market/ticker:{symbol}` — Subscribe to best bid/offer ticker pushes."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from typed_kucoin.core import StreamEndpoint, TimestampMillis


class TickerUpdate(TypedDict):
  """One best-bid/offer snapshot for a symbol."""

  sequence: str
  """Sequence number."""
  price: str
  """Last traded price."""
  size: str
  """Last traded amount."""
  bestAsk: str
  bestAskSize: str
  bestBid: str
  bestBidSize: str
  time: TimestampMillis
  """Matching time of the latest transaction."""


validate_update = validator(TickerUpdate)


class Ticker(StreamEndpoint):
  """Subscribe to `/market/ticker:{symbol}` — mixed into `Market`, the product exposing
  `streams.spot_margin.ticker`."""

  def ticker(
    self, symbol: str, *, validate: bool | None = None
  ) -> StreamManager[TickerUpdate, Any, Any]:
    """Subscribe to best-bid/offer ticker pushes for one symbol, pushed once every 100ms.

    Args:
      symbol: Symbol name, for example `BTC-USDT`.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/market/ticker:{symbol}', validator=validate_update, validate=validate
    )
