from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class AmendedOrder(TypedDict):
  """The order after amendment."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  orderListId: int
  """Id of the order list this order belongs to, or -1 if it is not part of one."""
  origClientOrderId: str
  """Client order id of the order prior to the amendment."""
  clientOrderId: str
  """Client order id of the order after the amendment."""
  price: str
  """Order price after the amendment."""
  qty: str
  """Order quantity after the amendment."""
  executedQty: str
  """Cumulative filled quantity."""
  preventedQty: str
  """Order quantity that expired due to self-trade prevention."""
  quoteOrderQty: str
  """Quote asset quantity implied by the order."""
  cumulativeQuoteQty: str
  """Cumulative quote asset transacted quantity."""
  status: Literal[
    'NEW',
    'PENDING_NEW',
    'PARTIALLY_FILLED',
    'FILLED',
    'CANCELED',
    'PENDING_CANCEL',
    'REJECTED',
    'EXPIRED',
    'EXPIRED_IN_MATCH',
  ]
  """Order status after the amendment."""
  timeInForce: Literal['GTC', 'IOC', 'FOK']
  """Time in force."""
  type: Literal[
    'LIMIT',
    'MARKET',
    'STOP_LOSS',
    'STOP_LOSS_LIMIT',
    'TAKE_PROFIT',
    'TAKE_PROFIT_LIMIT',
    'LIMIT_MAKER',
  ]
  """Order type."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  workingTime: NotRequired[Timestamp]
  """Time the order started working on the order book. Absent when the order is part of an order list still pending execution (e.g. an OTO's pending leg)."""
  selfTradePreventionMode: Literal[
    'NONE', 'EXPIRE_MAKER', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'DECREMENT', 'TRANSFER'
  ]
  """Self-trade prevention mode in effect for the order."""


class OrderListOrder(TypedDict):
  """One order belonging to an order list."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  clientOrderId: str
  """Client order id."""


class AmendListStatus(TypedDict):
  """The order list this amended order belongs to, present only when it is part of one."""

  orderListId: int
  """Id of the order list."""
  contingencyType: Literal['OCO', 'OTO']
  """Contingency type of the order list."""
  listOrderStatus: Literal['EXECUTING', 'ALL_DONE', 'REJECT']
  """Status of the orders within the order list."""
  listClientOrderId: str
  """Client order id of the order list."""
  symbol: str
  """Trading pair symbol."""
  orders: list[OrderListOrder]
  """Orders belonging to this order list."""


class OrderAmendResult(TypedDict):
  """Result of amending the order's quantity."""

  transactTime: Timestamp
  """Time the amendment was processed."""
  executionId: int
  """Execution id of the amendment."""
  amendedOrder: AmendedOrder
  listStatus: NotRequired[AmendListStatus]


class OrderAmendKeepPriority(WsRpcEndpoint):
  """Order Amend Keep Priority"""

  async def order_amend_keep_priority(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    orig_client_order_id: str | None = None,
    new_client_order_id: str | None = None,
    new_qty: str,
    validate: bool | None = None,
  ) -> OrderAmendResult:
    """Reduce the quantity of an existing open order without losing its priority on the order book. Either orderId or origClientOrderId must be sent.

    Args:
      symbol: Trading pair symbol.
      order_id: Id of the order to amend. Either orderId or origClientOrderId must be sent.
      orig_client_order_id: Client order id of the order to amend. Either orderId or origClientOrderId must be sent.
      new_client_order_id: Client order id for the order after being amended. If not sent, one is randomly generated. The current clientOrderId may be reused by sending it as newClientOrderId.
      new_qty: New order quantity. Must be greater than 0 and less than the order's current quantity.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#order-amend-keep-priority-trade)
    """
    params: dict = {
      'symbol': symbol,
      'newQty': new_qty,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    _Response = OrderAmendResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'order.amend.keepPriority', params=params, validator=_validator, validate=validate
    )
