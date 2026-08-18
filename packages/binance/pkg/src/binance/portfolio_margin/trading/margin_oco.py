from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmMarginAccountsOcoOrders(TypedDict):
  """PmMarginAccountsOcoOrders."""

  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  clientOrderId: NotRequired[str]
  """Client Order ID."""


class PmMarginAccountsOco(TypedDict):
  """Retrieves a specific OCO based on provided optional parameters."""

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
  orders: NotRequired[list[PmMarginAccountsOcoOrders]]
  """Orders."""


class MarginOco(RpcEndpoint):
  """Query Margin Account's OCO"""

  async def margin_oco(
    self,
    *,
    order_list_id: int | None = None,
    orig_client_order_id: str | None = None,
    validate: bool | None = None,
  ) -> PmMarginAccountsOco:
    """Retrieves a specific OCO based on provided optional parameters.

    Args:
      order_list_id: Either `orderListId` or `listClientOrderId` must be provided.
      orig_client_order_id: `orderListId` or `listClientOrderId` must be provided.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-margin-accounts-oco)
    """
    params = {}
    if order_list_id is not None:
      params['orderListId'] = order_list_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    _Response = PmMarginAccountsOco
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/margin/orderList',
      params=params,
      validator=_validator,
      validate=validate,
    )
