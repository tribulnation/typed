from decimal import Decimal
from bit2me.core.endpoint import StreamEndpoint
from bit2me.core.transport.ws.trading import Reply
from typed_core.util import StreamManager
from typed_core.validation import validator
from typing_extensions import TypedDict
from bit2me.types import MillisTimestamp, OrderSide


class PublicTrade(TypedDict):
  """One trade executed on the public market."""

  side: OrderSide
  price: Decimal
  """Price the trade executed at."""
  amount: Decimal
  """Traded volume, in base currency."""
  timestamp: MillisTimestamp


validate_message = validator(PublicTrade)


class PublicTrades(StreamEndpoint):
  def public_trades(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[PublicTrade, Reply, Reply]:
    """Stream every trade executed on one market symbol.

    Args:
      symbol: Market symbol to subscribe to, for example `BTC/EUR`.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets)
    """
    return self.subscribe(
      'public-trades', {'symbol': symbol}, validator=validate_message, validate=validate
    )
