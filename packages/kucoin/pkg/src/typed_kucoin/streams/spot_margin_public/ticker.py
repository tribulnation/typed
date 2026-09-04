"""`/market/ticker:{symbol}` — Subscribe to best bid/offer ticker pushes."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from typed_kucoin.core import TimestampMillis
from typed_kucoin.core.endpoint.stream import PublicStreamEndpoint


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


class Ticker(PublicStreamEndpoint):
  """Subscribe to `/market/ticker:{symbol}` — mixed into `SpotMarginPublic`, the product
  exposing `streams.spot_margin_public.ticker`."""

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
    return self.client.subscribe(
      f'/market/ticker:{symbol}', validator=validate_update, validate=validate
    )
