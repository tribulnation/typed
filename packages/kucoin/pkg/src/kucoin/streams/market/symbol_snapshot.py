"""`/market/snapshot:{symbol}` — Subscribe to a full trading-pair statistics snapshot for one symbol, refreshed once every 2 seconds."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import SymbolStats, WsSubscriptionAck
from kucoin.core import StreamEndpoint


class SymbolSnapshotUpdate(TypedDict):
  """One symbol snapshot -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section). This is itself a `{sequence, data}` wrapper around the real statistics object -- KuCoin nests an inner `data` here, distinct from the outer frame's `data` the transport already unwrapped."""

  sequence: str
  """Sequence number of this snapshot."""
  data: SymbolStats


_Type = SymbolSnapshotUpdate
validate_update = validator[_Type](_Type)  # type: ignore


class SymbolSnapshot(StreamEndpoint):
  """Subscribe to `/market/snapshot:{symbol}` — mixed into `Market`, the product exposing `streams.spot_margin.symbol_snapshot`."""

  def symbol_snapshot(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[SymbolSnapshotUpdate, Any, Any]:
    """Subscribe to a full trading-pair statistics snapshot for one symbol, refreshed once every 2 seconds.

    Args:
      symbol: Trading pair symbol, for example `BTC-USDT`.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/market/snapshot:{symbol}',
      validator=validate_update,
      validate=validate,
    )
