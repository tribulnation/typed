from decimal import Decimal
from datetime import datetime
from bit2me.core.endpoint import StreamEndpoint
from bit2me.core.transport.ws.trading import Reply
from typed_core.util import StreamManager
from typed_core.validation import validator
from typing_extensions import NotRequired, TypedDict
from bit2me.types import MillisTimestamp, OrderSide


class TradeFee(TypedDict):
  """Fee charged for this trade."""

  cost: Decimal
  """Fee charged, in `currency`."""
  currency: str
  """Currency the fee was charged in."""
  rate: NotRequired[Decimal]
  """Fee rate applied, as a fraction of the trade cost."""


class MyTradeUpdate(TypedDict):
  """One trade executed against the authenticated user's orders."""

  id: str
  """Trade identifier."""
  userId: NotRequired[str]
  """Owner of the filled order."""
  symbol: str
  """Market symbol the trade executed on."""
  order: NotRequired[str]
  """Identifier of the order this trade filled."""
  side: OrderSide
  price: Decimal
  """Price the trade executed at."""
  amount: Decimal
  """Traded volume, in base currency."""
  cost: NotRequired[Decimal]
  """Total cost of the trade, in quote currency."""
  timestamp: NotRequired[MillisTimestamp]
  datetime: NotRequired[datetime]
  """When the trade executed, in ISO 8601."""
  isMaker: NotRequired[bool]
  """Whether the user was the maker of the trade."""
  clientOrderId: NotRequired[str | None]
  """Client-supplied identifier of the filled order, or null."""
  fee: NotRequired[TradeFee]


validate_message = validator(MyTradeUpdate)


class MyTrades(StreamEndpoint):
  def my_trades(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> StreamManager[MyTradeUpdate, Reply, Reply]:
    """Stream trades executed against the authenticated user's orders.

    Args:
      symbol: Market symbol to filter on; omit to receive every symbol.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets)
    """
    return self.authed_subscribe(
      'my-trades', {'symbol': symbol}, validator=validate_message, validate=validate
    )
