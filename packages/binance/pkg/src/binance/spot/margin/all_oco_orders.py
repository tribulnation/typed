from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class MarginOrderListOrder(TypedDict):
  """One order belonging to the order list, identified minimally."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""


class MarginOrderList(TypedDict):
  """A margin order list (OCO or OTO), identified without its per-leg order reports."""

  orderListId: int
  """Id of the order list."""
  contingencyType: Literal['OCO', 'OTO']
  """Contingency type of the order list. Despite the endpoint's docs title ('Query Margin Account's all OCO'), this account's real response also included OTO order lists -- `OTO` added to the enum from that live evidence."""
  listStatusType: Literal['RESPONSE', 'EXEC_STARTED', 'UPDATED', 'ALL_DONE']
  """Status of the order list."""
  listOrderStatus: Literal['EXECUTING', 'ALL_DONE', 'REJECT']
  """Execution status of the order list."""
  listClientOrderId: str
  """Client id for the entire order list, either caller-supplied or venue-generated."""
  transactionTime: Timestamp
  """Time the order list was created."""
  symbol: str
  """Trading pair symbol."""
  isIsolated: bool
  """Whether the order list belongs to an isolated margin account."""
  orders: list[MarginOrderListOrder]
  """The above and below legs making up the OCO, identified minimally."""


class AllOcoOrders(RpcEndpoint):
  """Query all margin OCO order lists for the account, optionally filtered by symbol, order-list id or time range."""

  async def all_oco_orders(
    self,
    *,
    is_isolated: Literal['TRUE', 'FALSE'] | None = None,
    symbol: str | None = None,
    from_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[MarginOrderList]:
    """Query all margin OCO order lists for the account, optionally filtered by symbol, order-list id or time range.

    Args:
      is_isolated: Margin account type for this order: isolated when TRUE, crossed (default) when FALSE.
      symbol: Trading pair symbol. Mandatory for isolated margin, not supported for crossed margin.
      from_id: Only return order lists with an id >= this value. If supplied, neither startTime nor endTime can be provided.
      start_time: Only return order lists created at or after this time.
      end_time: Only return order lists created at or before this time.
      limit: Maximum number of order lists to return. Default 500; max 1000.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-margin-accounts-all-oco)
    """
    params = {}
    if is_isolated is not None:
      params['isIsolated'] = is_isolated
    if symbol is not None:
      params['symbol'] = symbol
    if from_id is not None:
      params['fromId'] = from_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[MarginOrderList]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/allOrderList',
      params=params,
      validator=_validator,
      validate=validate,
    )
