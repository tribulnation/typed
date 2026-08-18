"""`/contractMarket/advancedOrders` — Subscribe to the authenticated account's futures stop-order (advanced order) lifecycle pushes, across every contract symbol -- fires when a stop order enters the order book (`open`) or is triggered (`triggered`) or canceled (`cancel`). After triggering, the resulting regular order's lifecycle is reported on `streams.futures.order`/`streams.futures.all_orders` instead, not this channel."""

from typing_extensions import Any, Literal
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class FuturesStopOrderEvent(TypedDict):
  """One futures stop-order lifecycle push -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.authed_subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  orderId: str
  """Stop order id assigned by the trading system."""
  symbol: str
  """Contract symbol, for example `XBTUSDTM`."""
  orderType: Literal['stop']
  """User-specified order type -- always `stop` on this channel."""
  side: Literal['buy', 'sell']
  """Order side."""
  size: int
  """Order size, in contracts."""
  orderPrice: str
  """Limit price the resulting order executes at once triggered."""
  stop: Literal['up', 'down']
  """Trigger direction: `up` (trigger when the mark/index/trade price rises to `stopPrice`) or `down` (trigger when it falls to `stopPrice`)."""
  stopPrice: str
  """Trigger price."""
  stopPriceType: Literal['TP', 'IP', 'MP']
  """Price reference the trigger watches."""
  marginMode: Literal['ISOLATED', 'CROSS']
  """Margin mode the stop order was placed under."""
  type: Literal['open', 'triggered', 'cancel']
  """Event driving this push: `open` (entered the order book, awaiting trigger), `triggered` (trigger condition met, a regular order was placed -- see `streams.futures.order`/`all_orders` for its lifecycle), `cancel` (canceled before triggering)."""
  createdAt: int
  """Unix milliseconds when the stop order was created."""
  ts: int
  """Unix nanoseconds when this push was generated."""


_Type = FuturesStopOrderEvent
validate_update = validator[_Type](_Type)  # type: ignore


class StopOrder(StreamEndpoint):
  """Subscribe to `/contractMarket/advancedOrders` — mixed into `Private`, the product exposing `streams.futures.stop_order`."""

  def stop_order(
    self,
    *,
    validate: bool | None = None,
  ) -> StreamManager[FuturesStopOrderEvent, Any, Any]:
    """Subscribe to the authenticated account's futures stop-order (advanced order) lifecycle pushes, across every contract symbol -- fires when a stop order enters the order book (`open`) or is triggered (`triggered`) or canceled (`cancel`). After triggering, the resulting regular order's lifecycle is reported on `streams.futures.order`/`streams.futures.all_orders` instead, not this channel.

    Args:
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    Raises:
      AuthError: This connection has no credentials — this is a private channel, unreachable from a `public=True` client.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.authed_subscribe(
      '/contractMarket/advancedOrders',
      validator=validate_update,
      validate=validate,
    )
