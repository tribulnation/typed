"""`/contractMarket/execution:{symbol}` — Subscribe to real-time match (trade) execution pushes for one futures contract -- one push per order matched."""

from typing_extensions import Any, Literal
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class FuturesExecutionUpdate(TypedDict):
  """One match execution -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  symbol: str
  """Contract symbol, for example `XBTUSDTM`."""
  sequence: int
  """Sequence number of this match."""
  side: Literal['buy', 'sell']
  """Taker side of this match."""
  size: int
  """Quantity matched, in contracts."""
  price: str
  """Match price."""
  takerOrderId: str
  """Identifier of the taker order."""
  makerOrderId: str
  """Identifier of the maker order."""
  tradeId: str
  """Identifier of this match."""
  ts: int
  """Timestamp of this push, in nanoseconds."""


_Type = FuturesExecutionUpdate
validate_update = validator[_Type](_Type)  # type: ignore


class Execution(StreamEndpoint):
  """Subscribe to `/contractMarket/execution:{symbol}` — mixed into `Market`, the product exposing `streams.futures.execution`."""

  def execution(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[FuturesExecutionUpdate, Any, Any]:
    """Subscribe to real-time match (trade) execution pushes for one futures contract -- one push per order matched.

    Args:
      symbol: Contract symbol to watch, for example `XBTUSDTM`.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/contractMarket/execution:{symbol}',
      validator=validate_update,
      validate=validate,
    )
