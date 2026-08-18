"""`/market/level2:{symbol}` — Subscribe to incremental full-depth order book changes for one symbol, in real time. A price level whose pushed `size` is `"0"` has been removed from the book entirely, per KuCoin's own maintenance note for this channel."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class OrderbookIncrementChanges(TypedDict):
  """Changed price levels on each side."""

  asks: list[tuple[str, str, str]]
  """Changed ask levels, each `[price, size, sequence]`. `size` of `"0"` removes the level."""
  bids: list[tuple[str, str, str]]
  """Changed bid levels, each `[price, size, sequence]`. `size` of `"0"` removes the level."""


class OrderbookIncrementUpdate(TypedDict):
  """One incremental full-depth order book change -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  changes: OrderbookIncrementChanges
  sequenceEnd: int
  """Last sequence number covered by this push."""
  sequenceStart: int
  """First sequence number covered by this push."""
  symbol: str
  """Trading pair symbol."""
  time: int
  """Unix milliseconds of this update."""


_Type = OrderbookIncrementUpdate
validate_update = validator[_Type](_Type)  # type: ignore


class OrderbookIncrement(StreamEndpoint):
  """Subscribe to `/market/level2:{symbol}` — mixed into `Market`, the product exposing `streams.spot_margin.orderbook_increment`."""

  def orderbook_increment(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[OrderbookIncrementUpdate, Any, Any]:
    """Subscribe to incremental full-depth order book changes for one symbol, in real time. A price level whose pushed `size` is `"0"` has been removed from the book entirely, per KuCoin's own maintenance note for this channel.

    Args:
      symbol: Trading pair symbol, for example `BTC-USDT`. The venue's own topic syntax accepts a comma-joined list of up to 100 symbols on one subscription; this spec models the single-symbol form.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.subscribe(
      f'/market/level2:{symbol}',
      validator=validate_update,
      validate=validate,
    )
