from decimal import Decimal
from datetime import datetime
from bit2me.core.endpoint import StreamEndpoint
from bit2me.core.transport.ws.trading import Reply
from typed_core.util import StreamManager
from typed_core.validation import validator
from typing_extensions import NotRequired, TypedDict
from bit2me.types import MillisTimestamp


class OrderBookUpdate(TypedDict):
  """Level 2 order book snapshot for one symbol."""

  symbol: str
  """Market symbol the book belongs to."""
  bids: list[tuple[Decimal, Decimal]]
  """Buy levels, best price first."""
  asks: list[tuple[Decimal, Decimal]]
  """Sell levels, best price first."""
  nonce: MillisTimestamp
  timestamp: NotRequired[MillisTimestamp]
  datetime: NotRequired[datetime]
  """When Bit2Me produced the snapshot, in ISO 8601."""


validate_message = validator(OrderBookUpdate)


class OrderBook(StreamEndpoint):
  def order_book(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[OrderBookUpdate, Reply, Reply]:
    """Stream level 2 order book snapshots for one market symbol.

    Args:
      symbol: Market symbol to subscribe to, for example `BTC/EUR`.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets)
    """
    return self.subscribe(
      'order-book', {'symbol': symbol}, validator=validate_message, validate=validate
    )
