"""`/market/candles:{symbol}_{type}` — Subscribe to K-Line (candle) updates for one symbol and interval, in real time -- the current, still-forming candle is pushed on every trade that updates it."""

from typing_extensions import Any, Literal
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class KlineUpdate(TypedDict):
  """One K-Line update -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  symbol: str
  """Trading pair symbol."""
  candles: tuple[str, str, str, str, str, str, str]
  """The current (possibly still-forming) candle."""
  time: int
  """Unix nanoseconds when this push was generated -- not the candle's own time (see `candles[0]`)."""


_Type = KlineUpdate
validate_update = validator[_Type](_Type)  # type: ignore


class Klines(StreamEndpoint):
  """Subscribe to `/market/candles:{symbol}_{type}` — mixed into `Market`, the product exposing `streams.spot_margin.klines`."""

  def klines(
    self,
    symbol: str,
    type: Literal[
      '1min',
      '3min',
      '15min',
      '30min',
      '1hour',
      '2hour',
      '4hour',
      '6hour',
      '8hour',
      '12hour',
      '1day',
      '1week',
    ],
    *,
    validate: bool | None = None,
  ) -> StreamManager[KlineUpdate, Any, Any]:
    """Subscribe to K-Line (candle) updates for one symbol and interval, in real time -- the current, still-forming candle is pushed on every trade that updates it.

    Args:
      symbol: Trading pair symbol, for example `BTC-USDT`.
      type: Candle interval.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/market/candles:{symbol}_{type}',
      validator=validate_update,
      validate=validate,
    )
