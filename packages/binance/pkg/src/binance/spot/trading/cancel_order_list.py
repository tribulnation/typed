from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class CancelOrderListOrderReport(TypedDict):
  """One order-list leg's cancellation acknowledgement."""

  symbol: str
  """Trading pair symbol."""
  origClientOrderId: str
  """Client order id of the order as it was before this cancellation."""
  orderId: int
  """Order id."""
  orderListId: int
  """Id of the order list this order belongs to."""
  clientOrderId: str
  """Client id assigned to this cancellation request."""
  transactTime: Timestamp
  """Time the cancellation was processed."""
  price: str
  """Order price."""
  origQty: str
  """Original order quantity."""
  executedQty: str
  """Cumulative filled quantity."""
  origQuoteOrderQty: str
  """Original quoteOrderQty, or "0" when quoteOrderQty was not used."""
  cummulativeQuoteQty: str
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
  """Order status."""
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
  selfTradePreventionMode: Literal[
    'NONE', 'EXPIRE_MAKER', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'DECREMENT', 'TRANSFER'
  ]
  """Self-trade prevention mode in effect for the order."""
  stopPrice: NotRequired[str]
  """Price at which the algorithmic order triggers. Present for STOP_LOSS, TAKE_PROFIT, STOP_LOSS_LIMIT and TAKE_PROFIT_LIMIT orders."""
  icebergQty: NotRequired[str]
  """Quantity for the iceberg order. Present only when an iceberg quantity was sent in the request."""
  strategyId: NotRequired[int]
  """Id labeling the order strategy this order is part of. Present when a strategy id was sent in the request."""
  strategyType: NotRequired[int]
  """Type labeling the order strategy this order is part of. Present when a strategy type was sent in the request."""
  trailingDelta: NotRequired[int]
  """Delta price change required before order activation. Present for trailing stop orders."""
  trailingTime: NotRequired[Timestamp]
  """Time the trailing order became active and started tracking price changes. Present only for trailing stop orders."""
  pegPriceType: NotRequired[Literal['PRIMARY_PEG', 'MARKET_PEG']]
  """Peg reference type. Present only for pegged orders."""
  pegOffsetType: NotRequired[Literal['PRICE_LEVEL']]
  """Peg offset type. Present only for pegged orders that requested one."""
  pegOffsetValue: NotRequired[int]
  """Peg offset value. Present only for pegged orders that requested one."""
  peggedPrice: NotRequired[str]
  """Current price the order is pegged at. Present only for pegged orders, once determined."""
  expiryReason: NotRequired[
    Literal[
      'NONE',
      'REJECTED',
      'EXCHANGE_CANCELED',
      'OCO_TRIGGER',
      'OTO_PHASE_ONE_EXPIRED',
      'UNFILLED_IOC_QUANTITY_EXPIRED',
      'UNFILLED_FOK_ORDER_EXPIRED',
      'INSUFFICIENT_LIQUIDITY',
      'EXECUTION_RULE_PRICE_RANGE_EXCEEDED',
    ]
  ]
  """Cause of the order's expiration. Present when the order has expired."""
  preventedMatchId: NotRequired[int]
  """Id of a prevented match, usable together with symbol to query it. Present only when the order expired due to self-trade prevention."""
  preventedQuantity: NotRequired[str]
  """Order quantity that expired due to self-trade prevention. Present only when the order expired due to self-trade prevention."""


class OrderListOrder(TypedDict):
  """One order belonging to the order list, identified minimally."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""


class CancelOrderListResult(TypedDict):
  """Result of canceling an entire order list."""

  orderListId: int
  """Id of the canceled order list."""
  contingencyType: Literal['OCO', 'OTO']
  """Contingency type of the order list."""
  listStatusType: Literal['RESPONSE', 'EXEC_STARTED', 'UPDATED', 'ALL_DONE']
  """Status of the order list."""
  listOrderStatus: Literal['EXECUTING', 'ALL_DONE', 'REJECT']
  """Execution status of the order list."""
  listClientOrderId: str
  """Client id for the entire order list, either caller-supplied or venue-generated."""
  transactionTime: Timestamp
  """Time the cancellation was processed."""
  symbol: str
  """Trading pair symbol."""
  orders: list[OrderListOrder]
  """The orders that made up the canceled order list, identified minimally."""
  orderReports: list[CancelOrderListOrderReport]
  """Per-leg cancellation acknowledgements."""


class CancelOrderList(RpcEndpoint):
  """Cancel an entire order list. Canceling an individual order that belongs to an order list cancels the entire order list. If both orderListId and listClientOrderId are provided, orderListId is searched first, then listClientOrderId is checked against that result; the request is rejected if both conditions are not met."""

  async def cancel_order_list(
    self,
    *,
    symbol: str,
    order_list_id: int | None = None,
    list_client_order_id: str | None = None,
    new_client_order_id: str | None = None,
    validate: bool | None = None,
  ) -> CancelOrderListResult:
    """Cancel an entire order list. Canceling an individual order that belongs to an order list cancels the entire order list. If both orderListId and listClientOrderId are provided, orderListId is searched first, then listClientOrderId is checked against that result; the request is rejected if both conditions are not met.

    Args:
      symbol: Trading pair symbol.
      order_list_id: Id of the order list to cancel. Either orderListId or listClientOrderId must be provided.
      list_client_order_id: Client id of the order list to cancel. Either orderListId or listClientOrderId must be provided.
      new_client_order_id: Client id to uniquely identify this cancel. Automatically generated if not sent.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
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
    _Response = CancelOrderListResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/api/v3/orderList',
      params=params,
      validator=_validator,
      validate=validate,
    )
