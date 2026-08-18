"""`/spotMarket/advancedOrders` — Subscribe to the authenticated account's stop-order (advanced order) lifecycle pushes -- fires when a stop order is opened, canceled, matched, filled, updated, or received by the matching system."""

from typing_extensions import Any, Literal
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class StopOrderEvent(TypedDict):
  """One stop-order lifecycle push -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.authed_subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  orderId: str
  """Stop order id assigned by the trading system."""
  orderPrice: str
  """Limit price the order executes at once triggered."""
  orderType: Literal['stop']
  """User-specified order type -- always `stop` on this channel."""
  side: Literal['buy', 'sell']
  """Order side."""
  size: str
  """Order size."""
  stop: Literal['loss', 'entry', 'l_l_o', 'l_s_o', 'e_l_o', 'e_s_o', 'tso']
  """Stop order flavor: `loss` (stop-loss), `entry` (take-profit), `l_l_o`/`l_s_o` (limit/trigger legs of a limit stop-loss OCO order), `e_l_o`/`e_s_o` (limit/trigger legs of a limit stop-profit OCO order), `tso` (trailing/moving stop-loss order)."""
  stopPrice: str
  """Trigger price."""
  symbol: str
  """Trading pair symbol, for example `BTC-USDT`."""
  tradeType: Literal['TRADE', 'MARGIN_TRADE', 'MARGIN_ISOLATED_TRADE']
  """Trading account the order belongs to."""
  ts: int
  """Unix nanoseconds when this push was generated."""
  type: Literal['received', 'open', 'match', 'update', 'filled', 'cancel']
  """Event driving this push: `received` (entered the matching system), `open` (resting, awaiting trigger), `match` (matched against a counterparty), `update` (modified -- partial cancel or self-trade-prevention trigger), `filled` (fully executed), `cancel` (canceled)."""
  createdAt: int
  """Unix milliseconds when the stop order was created."""


_Type = StopOrderEvent
validate_update = validator[_Type](_Type)  # type: ignore


class StopOrder(StreamEndpoint):
  """Subscribe to `/spotMarket/advancedOrders` — mixed into `Private`, the product exposing `streams.spot_margin.stop_order`."""

  def stop_order(
    self,
    *,
    validate: bool | None = None,
  ) -> StreamManager[StopOrderEvent, Any, Any]:
    """Subscribe to the authenticated account's stop-order (advanced order) lifecycle pushes -- fires when a stop order is opened, canceled, matched, filled, updated, or received by the matching system.

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
      '/spotMarket/advancedOrders',
      validator=validate_update,
      validate=validate,
    )
