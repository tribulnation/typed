"""`POST /api/v3/hf/margin/oco-order` — Add OCO Order."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class AddMarginOcoOrderRequest(TypedDict):
  clientOid: str
  """Client-generated unique order id (a UUID is recommended): letters, digits, underscores and hyphens only, max 40 characters."""
  symbol: str
  """Trading pair, e.g. `ETH-USDT`."""
  side: Literal['buy', 'sell']
  """Order direction, shared by both legs."""
  price: str
  """Price for the upper leg (a plain limit order at this price)."""
  size: str
  """Order quantity, shared by both legs."""
  stopPrice: str
  """Trigger price for the lower leg."""
  limitPrice: str
  """Limit price the lower leg executes at once `stopPrice` triggers."""
  remark: NotRequired[str]
  """Order placement remark, max 20 ASCII characters."""
  isIsolated: NotRequired[bool]
  """`true` places the order against isolated margin, `false` (default) against cross margin."""
  autoBorrow: NotRequired[bool]
  """Auto-borrow the shortfall at the lowest market rate once a leg triggers/fills."""
  autoRepay: NotRequired[bool]
  """Auto-repay borrowed assets once a triggered/filled leg closes a position."""


class AddMarginOcoOrderResult(TypedDict):
  orderId: str
  """System-generated id for the OCO order group, used for later lookup/cancellation."""


_Type = AddMarginOcoOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class Add(RpcEndpoint):
  """`Add OCO Order` — mixed into `OcoOrders`, the product exposing `margin.oco_orders.add`."""

  async def add(
    self,
    add_margin_oco_order_request: AddMarginOcoOrderRequest,
    *,
    validate: bool | None = None,
  ) -> AddMarginOcoOrderResult:
    """Place an OCO (One-Cancels-the-Other) order into the margin high-frequency (hf) trading system, against cross-margin or isolated-margin: two linked leg orders -- an upper limit leg priced at `price`, and a lower leg that triggers at `stopPrice` and executes as a limit order at `limitPrice` -- where a fill or cancellation of either leg cancels the other. Maximum 20 untriggered stop/OCO orders per symbol per account.

    Args:
      add_margin_oco_order_request: OCO order placement parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/hf/margin/oco-order',
      json=add_margin_oco_order_request,
      validator=adapter,
      validate=validate,
    )
