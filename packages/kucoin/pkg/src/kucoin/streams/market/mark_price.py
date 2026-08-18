"""`/indicator/markPrice:{symbol}` — Subscribe to the mark price used for margin-trading interest/liquidation calculations, for one margin symbol -- pushed once every second. Documented under KuCoin's Margin Trading public channels, but reached over the same Spot/Margin WebSocket instance as every other channel in this subdivision (`spec/core.md`'s WebSocket section: one connection, two topic families)."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class MarkPriceUpdate(TypedDict):
  """One mark-price tick -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  symbol: str
  """Margin indicator symbol, quote-currency-first (e.g. `USDT-BTC`)."""
  granularity: int
  """Push interval, in milliseconds."""
  timestamp: int
  """Unix milliseconds of this tick."""
  value: float
  """Mark price."""


_Type = MarkPriceUpdate
validate_update = validator[_Type](_Type)  # type: ignore


class MarkPrice(StreamEndpoint):
  """Subscribe to `/indicator/markPrice:{symbol}` — mixed into `Market`, the product exposing `streams.spot_margin.mark_price`."""

  def mark_price(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[MarkPriceUpdate, Any, Any]:
    """Subscribe to the mark price used for margin-trading interest/liquidation calculations, for one margin symbol -- pushed once every second. Documented under KuCoin's Margin Trading public channels, but reached over the same Spot/Margin WebSocket instance as every other channel in this subdivision (`spec/core.md`'s WebSocket section: one connection, two topic families).

    Args:
      symbol: Margin indicator symbol. The venue names this **quote-currency-first** (e.g. `USDT-BTC`), the reverse of a normal spot trading-pair symbol (`BTC-USDT`) -- confirmed both by the docs' own example and this pass's live capture. The venue's own topic syntax also accepts a comma-joined list of symbols; this spec models the single-symbol form.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/indicator/markPrice:{symbol}',
      validator=validate_update,
      validate=validate,
    )
