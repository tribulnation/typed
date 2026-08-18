from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmCancelMarginAccountOcoOrdersOrders(TypedDict):
  """PmCancelMarginAccountOcoOrdersOrders."""

  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  clientOrderId: NotRequired[str]
  """Client Order ID."""


class PmCancelMarginAccountOcoOrders(TypedDict):
  """Cancel Margin Account OCO Orders."""

  orderListId: NotRequired[int]
  """Order List ID."""
  contingencyType: NotRequired[str]
  """Contingency Type."""
  listStatusType: NotRequired[str]
  """List Status Type."""
  listOrderStatus: NotRequired[str]
  """List Order Status."""
  listClientOrderId: NotRequired[str]
  """List Client Order ID."""
  transactionTime: NotRequired[Timestamp]
  """Transaction Time."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  orders: NotRequired[list[PmCancelMarginAccountOcoOrdersOrders]]
  """Orders."""


class CancelMarginOco(RpcEndpoint):
  """Cancel Margin Account OCO Orders"""

  async def cancel_margin_oco(
    self,
    *,
    symbol: str,
    order_list_id: int | None = None,
    list_client_order_id: str | None = None,
    new_client_order_id: str | None = None,
    validate: bool | None = None,
  ) -> PmCancelMarginAccountOcoOrders:
    """Cancel Margin Account OCO Orders.

    Args:
      symbol: Symbol.
      order_list_id: Either `orderListId` or `listClientOrderId` must be provided.
      list_client_order_id: Either `orderListId` or `listClientOrderId` must be provided.
      new_client_order_id: Used to uniquely identify this cancel request.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#cancel-margin-account-oco-orders)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_list_id is not None:
      params['orderListId'] = order_list_id
    if list_client_order_id is not None:
      params['listClientOrderId'] = list_client_order_id
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    _Response = PmCancelMarginAccountOcoOrders
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/papi/v1/margin/orderList',
      params=params,
      validator=_validator,
      validate=validate,
    )
