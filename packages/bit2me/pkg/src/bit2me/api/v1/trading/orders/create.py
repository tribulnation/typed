from typing_extensions import NotRequired, TypedDict
from bit2me.types import OrderResponse, OrderSide, OrderType, PostOnlyParam, TimeInForce
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class TradingOrdersCreateRequest(TypedDict):
  side: OrderSide
  symbol: str
  """The market symbol"""
  price: NotRequired[str]
  stopPrice: NotRequired[str]
  amount: str
  orderType: OrderType
  clientOrderId: NotRequired[str]
  """Optional client internal order identifier"""
  postOnly: NotRequired[PostOnlyParam]
  timeInForce: NotRequired[TimeInForce]
  amountInQuote: NotRequired[bool]
  """Option to express volume in quote currency. This option is supported only for market orders. When using this parameter, Bit2Me calculates market price of the asset and immediately executes the order. This means that 100% precision is not guaranteed. When using this feature, you acknowledge that you understand how this works and accept that the differences arising from this method are not an error and are not Bit2Me responsibility to fix or provide you with additional information."""


validate_response = validator(OrderResponse)


class Create(RpcEndpoint):
  async def create(
    self,
    trading_orders_create_request: TradingOrdersCreateRequest,
    *,
    validate: bool | None = None,
  ) -> OrderResponse:
    """Place a new order.

    See `GET /v1/trading/market-config` for the available trading assets, their price and quantity precisions, and order minimums.

    Args:
      trading_orders_create_request: Order parameters: side, market, amount, and order-type-specific price/timing fields.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/trading/POST/v1/trading/order)
    """
    return await self.authed_request(
      'POST',
      '/v1/trading/order',
      json=trading_orders_create_request,
      validator=validate_response,
      validate=validate,
    )
