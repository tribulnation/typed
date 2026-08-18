"""Hand-written PoC for the `trading_ws` surface: one public subscription
(`order_book`), one private subscription (`my_balance`), one command
(`cancel_all_orders`) — the three shapes `trading_ws` needs to prove. Stands in for
the full generated set (`add-order(s)`, `cancel-order(s)`,
`auto-cancel-orders-on-disconnection`, `authenticate`, `public-trades`, `my-orders`,
`my-trades`, `my-working-capital`, `executions`) the codegen revamp will produce.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing_extensions import NotRequired

from typed_core.util import StreamManager

from bit2me.core.endpoint import RpcEndpoint, StreamEndpoint
from bit2me.core.types import Timestamp
from typed_core.validation import TypedDict, validator
from bit2me.core.transport.ws.trading import Reply, TradingWsClient

OrderBookLevel = tuple[Decimal, Decimal]
"""One price level: `(price, volume)`, per the spec's `prefixItems` tuple — not a
dict, despite `price`/`volume` reading like field names in the upstream docs."""


class OrderBookUpdate(TypedDict):
  """Level 2 order book snapshot for one symbol."""

  symbol: NotRequired[str]
  bids: NotRequired[list[OrderBookLevel]]
  """Buy levels, best price first."""
  asks: NotRequired[list[OrderBookLevel]]
  """Sell levels, best price first."""
  nonce: NotRequired[Timestamp]
  """Monotonic revision of the book, for gap detection."""


class CurrencyBalance(TypedDict):
  """Balance held in one currency."""

  currency: NotRequired[str]
  balance: NotRequired[Decimal]
  """Balance available to trade."""
  blockedBalance: NotRequired[Decimal]
  """Balance reserved by resting orders."""


class MyBalanceUpdate(TypedDict):
  """The authenticated user's balances after one of them changed."""

  userId: NotRequired[str]
  balance: NotRequired[list[CurrencyBalance]]


validate_order_book = validator(OrderBookUpdate)
validate_my_balance = validator(MyBalanceUpdate)


@dataclass(kw_only=True, frozen=True)
class TradingWs(RpcEndpoint, StreamEndpoint):
  """Combines `RpcEndpoint` (for the six commands) and `StreamEndpoint` (for the
  channel subscriptions) since `trading_ws` is genuinely both — see `spec/core.md`.
  Redeclares `client` because `TradingWsClient` satisfies both parents' `RpcClient`/
  `StreamClient` protocols, which the dataclass field merge alone can't express."""

  client: TradingWsClient

  def order_book(
    self, symbol: str, *, validate: bool | None = None
  ) -> StreamManager[OrderBookUpdate, Reply, Reply]:
    """Stream level 2 order book snapshots for one market symbol.

    Args:
      symbol: Market symbol to subscribe to, for example `"BTC/EUR"`.
      validate: Whether to validate pushed payloads against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets)
    """
    return self.subscribe(
      'order-book', {'symbol': symbol}, validator=validate_order_book, validate=validate
    )

  def my_balance(
    self, *, validate: bool | None = None
  ) -> StreamManager[MyBalanceUpdate, Reply, Reply]:
    """Stream the authenticated user's balances whenever one of them changes.

    Args:
      validate: Whether to validate pushed payloads against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets)
    """
    return self.authed_subscribe(
      'my-balance', validator=validate_my_balance, validate=validate
    )

  async def cancel_all_orders(
    self, *, symbol: str | None = None, side: str | None = None
  ) -> Reply:
    """Cancel every resting order, optionally scoped to one symbol and/or side.

    Args:
      symbol: Market symbol to scope the cancellation to; omit to cancel across
        every symbol.
      side: Order direction (`"buy"`/`"sell"`) to scope the cancellation to; omit to
        cancel both sides.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets#private-commands)
    """
    params: dict = {}
    if symbol is not None:
      params['symbol'] = symbol
    if side is not None:
      params['side'] = side
    return await self.authed_request('POST', 'cancel-all-orders', json=params)
