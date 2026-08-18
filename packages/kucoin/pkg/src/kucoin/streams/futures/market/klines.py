"""`/contractMarket/limitCandle:{symbol}_{type}` — Subscribe to K-line (candlestick) pushes for one futures contract and granularity, pushed roughly once a second while the current candle changes."""

from typing_extensions import Any, Literal
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class FuturesKlineUpdate(TypedDict):
  """The current (possibly still-forming) candle -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  symbol: str
  """Contract symbol, for example `XBTUSDTM`."""
  candles: tuple[str, str, str, str, str, str, str]
  """One candle row. Note the field order: open, close, high, low -- not the usual open/high/low/close."""
  time: int
  """Server timestamp of this push, in Unix milliseconds."""


_Type = FuturesKlineUpdate
validate_update = validator[_Type](_Type)  # type: ignore


class Klines(StreamEndpoint):
  """Subscribe to `/contractMarket/limitCandle:{symbol}_{type}` — mixed into `Market`, the product exposing `streams.futures.klines`."""

  def klines(
    self,
    symbol: str,
    type: Literal[
      '1min',
      '3min',
      '5min',
      '15min',
      '30min',
      '1hour',
      '2hour',
      '4hour',
      '8hour',
      '12hour',
      '1day',
      '1week',
      '1month',
    ],
    *,
    validate: bool | None = None,
  ) -> StreamManager[FuturesKlineUpdate, Any, Any]:
    """Subscribe to K-line (candlestick) pushes for one futures contract and granularity, pushed roughly once a second while the current candle changes.

    Args:
      symbol: Contract symbol to watch, for example `XBTUSDTM`.
      type: Candle granularity.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/contractMarket/limitCandle:{symbol}_{type}',
      validator=validate_update,
      validate=validate,
    )
