from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class OrderListOrder(TypedDict):
  """One order belonging to an order list."""

  symbol: str
  """Symbol this order was placed on."""
  orderId: int
  """Order ID assigned by Binance."""
  clientOrderId: str
  """Client-supplied order ID."""


class OrderListStatus(TypedDict):
  """A spot order list (OCO/OTO), in the shape returned by order-list-query commands."""

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
  transactionTime: Timestamp
  """Millisecond timestamp the order list was created or last updated."""
  symbol: str
  """Symbol this order list was placed on."""
  orders: list[OrderListOrder]
  """Orders belonging to this order list."""


class AllOrderLists(WsRpcEndpoint):
  """Account order list history"""

  async def all_order_lists(
    self,
    *,
    from_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[OrderListStatus]:
    """Query information about all your order lists, filtered by time range. If `startTime` and/or `endTime` are specified, `fromId` is ignored and order lists are filtered by the `transactionTime` of their last execution status update. If `fromId` is specified, order lists with order list ID >= `fromId` are returned. If no condition is specified, the most recent order lists are returned. The time between `startTime` and `endTime` can't be longer than 24 hours.

    Args:
      from_id: Order list ID to begin at (inclusive). Ignored if `startTime` and/or `endTime` are specified.
      start_time: Start of the time range, in milliseconds.
      end_time: End of the time range, in milliseconds.
      limit: Maximum number of order lists to return.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#account-order-list-history-user_data)
    """
    params = {}
    if from_id is not None:
      params['fromId'] = from_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[OrderListStatus]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'allOrderLists', params=params, validator=_validator, validate=validate
    )
