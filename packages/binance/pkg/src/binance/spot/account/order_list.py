from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class OrderListOrder(TypedDict):
  """One order belonging to an order list."""

  symbol: str
  """Symbol this order was placed on."""
  orderId: int
  """Order ID assigned by Binance."""
  clientOrderId: str
  """Client-supplied order ID."""


class SpotOrderList(TypedDict):
  """A spot order list (OCO/OTO)."""

  orderListId: int
  """Order list ID assigned by Binance."""
  contingencyType: Literal['OCO', 'OTO']
  """Contingency type of the order list."""
  listStatusType: Literal['RESPONSE', 'EXEC_STARTED', 'UPDATED', 'ALL_DONE']
  """Current status of the order list."""
  listOrderStatus: Literal['EXECUTING', 'ALL_DONE', 'REJECT']
  """Current status of the orders in the list."""
  listClientOrderId: str
  """Client-supplied order list ID."""
  transactionTime: int
  """Millisecond timestamp the order list was created or last updated."""
  symbol: str
  """Symbol this order list was placed on."""
  orders: list[OrderListOrder]
  """Orders belonging to this order list."""


class OrderList(RpcEndpoint):
  """Query order list"""

  async def order_list(
    self,
    *,
    order_list_id: int | None = None,
    orig_client_order_id: str | None = None,
    validate: bool | None = None,
  ) -> SpotOrderList:
    """Retrieve a specific order list based on the provided optional parameters. Either `orderListId` or `origClientOrderId` must be provided.

    Args:
      order_list_id: Query order list by `orderListId`. `orderListId` or `origClientOrderId` must be provided.
      orig_client_order_id: Query order list by `listClientOrderId`. `orderListId` or `origClientOrderId` must be provided.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
    """
    params = {}
    if order_list_id is not None:
      params['orderListId'] = order_list_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    _Response = SpotOrderList
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/api/v3/orderList', params=params, validator=_validator, validate=validate
    )
