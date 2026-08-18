"""`/contractMarket/level2Depth50:{symbol}` — Subscribe to the 50 best bid/ask price levels for one futures contract, pushed every 100ms while the book changes -- a full snapshot on every push, not an incremental update. No push when nothing has changed."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class FuturesOrderBookLevel50update(TypedDict):
  """The 50 best bid/ask levels, as a full snapshot -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  bids: list[tuple[str, int]]
  """Best 50 bid levels, best price first."""
  asks: list[tuple[str, int]]
  """Best 50 ask levels, best price first."""
  sequence: int
  """Sequence number of this snapshot."""
  timestamp: int
  """Server timestamp of this push, in Unix milliseconds."""
  ts: int
  """Identical to `timestamp` on every live capture this pass -- KuCoin's machine spec declares it as a separate required field regardless."""


_Type = FuturesOrderBookLevel50update
validate_update = validator[_Type](_Type)  # type: ignore


class OrderbookLevel50(StreamEndpoint):
  """Subscribe to `/contractMarket/level2Depth50:{symbol}` — mixed into `Market`, the product exposing `streams.futures.orderbook_level50`."""

  def orderbook_level50(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[FuturesOrderBookLevel50update, Any, Any]:
    """Subscribe to the 50 best bid/ask price levels for one futures contract, pushed every 100ms while the book changes -- a full snapshot on every push, not an incremental update. No push when nothing has changed.

    Args:
      symbol: Contract symbol to watch, for example `XBTUSDTM`.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/contractMarket/level2Depth50:{symbol}',
      validator=validate_update,
      validate=validate,
    )
