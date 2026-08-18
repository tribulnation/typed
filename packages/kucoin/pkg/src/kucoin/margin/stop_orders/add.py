"""`POST /api/v3/hf/margin/stop-order` — Add Stop Order."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class AddMarginStopOrderRequest(TypedDict):
  clientOid: NotRequired[str]
  """Unique order id created by the caller (a UUID is recommended) -- numbers, letters, underscores and hyphens only, up to 40 characters."""
  symbol: str
  """Trading pair, e.g. `KCS-USDT`."""
  side: Literal['buy', 'sell']
  """Order side."""
  type: Literal['limit', 'market']
  """Order type submitted once the stop triggers. `limit` requires `price` and `size`; `market` takes `size` or `funds` (not both) and no `price`."""
  stop: Literal['loss', 'entry']
  """Stop order trigger type. Unlike Spot's Add Stop Order (which never accepts this as a request field, deriving it server-side), this margin endpoint's own docs page and captured request example both show it as a real, required request field."""
  stopPrice: str
  """Trigger price. Once the market reaches this price, the order is submitted to the matching engine as a regular `type` order."""
  price: NotRequired[str]
  """Limit price for the order submitted once the stop triggers. Required when `type` is `limit`; unused for `market`."""
  size: NotRequired[str]
  """Order quantity, in the base currency, submitted once the stop triggers. Required when `type` is `limit`; for `market`, either `size` or `funds` is given, not both."""
  funds: NotRequired[str]
  """Order value, in the quote currency, submitted once the stop triggers. Only valid when `type` is `market`, as an alternative to `size`."""
  remark: NotRequired[str]
  """Order placement remark, up to 20 ASCII characters."""
  stp: NotRequired[Literal['CN', 'CO', 'CB', 'DC']]
  """Self-trade prevention strategy. Only `CB` appears in KuCoin's own request example; carried over from the sibling `margin.orders_hf.add`'s confirmed four-value set rather than independently confirmed on this endpoint's own docs page."""
  timeInForce: NotRequired[Literal['GTC', 'GTT', 'IOC', 'FOK']]
  """Time-in-force rule for the order submitted once the stop triggers. Only meaningful when `type` is `limit`."""
  isIsolated: NotRequired[bool]
  """`true` places the order against isolated margin, `false` (default) against cross margin."""
  autoBorrow: NotRequired[bool]
  """Auto-borrow the shortfall at the lowest market rate once the stop triggers."""
  autoRepay: NotRequired[bool]
  """Auto-repay borrowed assets once the triggered order closes a position."""


class AddMarginStopOrderResult(TypedDict):
  """Identifiers of the newly placed stop order. Unlike `margin.orders_hf.add`'s result, this carries no `loanApplyId`/`borrowSize` -- a stop order cannot borrow until it triggers into a real order."""

  orderId: str
  """Unique id generated for the new stop order, usable for later Get/Cancel calls."""
  clientOid: str
  """Client-provided order id, echoed back."""


_Type = AddMarginStopOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class Add(RpcEndpoint):
  """`Add Stop Order` — mixed into `StopOrders`, the product exposing `margin.stop_orders.add`."""

  async def add(
    self,
    add_margin_stop_order_request: AddMarginStopOrderRequest,
    *,
    validate: bool | None = None,
  ) -> AddMarginStopOrderResult:
    """Place a stop order into the margin high-frequency (hf) trading system, against cross-margin or isolated-margin. The order rests untriggered until the market reaches `stopPrice`, at which point it is submitted to the matching engine as a regular limit or market order. Maximum 20 untriggered stop orders per trading pair per account.

    Args:
      add_margin_stop_order_request: Stop order placement parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/hf/margin/stop-order',
      json=add_margin_stop_order_request,
      validator=adapter,
      validate=validate,
    )
