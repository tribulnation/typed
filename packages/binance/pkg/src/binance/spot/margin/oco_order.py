from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class MarginOrderListOrder(TypedDict):
  """One order belonging to the order list, identified minimally."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""


class MarginOcoOrder(TypedDict):
  """A margin OCO order list, identified without its per-leg order reports."""

  orderListId: int
  """Id of the order list."""
  contingencyType: Literal['OCO']
  """Contingency type of the order list."""
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


class OcoOrder(RpcEndpoint):
  """Query a single margin OCO order list. Either orderListId or origClientOrderId must be provided."""

  async def oco_order(
    self,
    *,
    is_isolated: Literal['TRUE', 'FALSE'] | None = None,
    symbol: str | None = None,
    order_list_id: int | None = None,
    orig_client_order_id: str | None = None,
    validate: bool | None = None,
  ) -> MarginOcoOrder:
    """Query a single margin OCO order list. Either orderListId or origClientOrderId must be provided.

    Args:
      is_isolated: Margin account type for this order: isolated when TRUE, crossed (default) when FALSE.
      symbol: Trading pair symbol. Mandatory for isolated margin, not supported for crossed margin.
      order_list_id: Id of the order list to query. Either orderListId or origClientOrderId must be provided.
      orig_client_order_id: Client id of the order list to query. Either orderListId or origClientOrderId must be provided.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-margin-accounts-oco)
    """
    params = {}
    if is_isolated is not None:
      params['isIsolated'] = is_isolated
    if symbol is not None:
      params['symbol'] = symbol
    if order_list_id is not None:
      params['orderListId'] = order_list_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    _Response = MarginOcoOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/orderList',
      params=params,
      validator=_validator,
      validate=validate,
    )
