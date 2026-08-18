from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class OrderStatus(TypedDict):
  """A spot order, in the shape returned by order-query commands."""

  symbol: str
  """Symbol this order was placed on."""
  orderId: int
  """Order ID assigned by Binance."""
  orderListId: int
  """ID of the order list this order belongs to, or -1 if it is not part of one."""
  clientOrderId: str
  """Client-supplied order ID."""
  price: str
  """Order price, as a decimal string."""
  origQty: str
  """Original order quantity, as a decimal string."""
  executedQty: str
  """Quantity that has been filled, as a decimal string."""
  cummulativeQuoteQty: str
  """Cumulative quote asset quantity filled, as a decimal string. For some historical orders this is negative, meaning the data is not available."""
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
  stopPrice: str
  """Stop price, as a decimal string. `0.0` when not a stop/take-profit order."""
  trailingDelta: NotRequired[int]
  """Delta for the order's trailing stop. Present only when trailingDelta was set on the order."""
  trailingTime: NotRequired[Timestamp]
  """Millisecond timestamp the trailing order became active and started tracking price changes, or -1 if not yet active. Present only when trailingDelta was set on the order."""
  icebergQty: str
  """Iceberg order quantity, as a decimal string. `0.0` when not an iceberg order."""
  time: Timestamp
  """Millisecond timestamp the order was created."""
  updateTime: Timestamp
  """Millisecond timestamp the order was last updated."""
  isWorking: bool
  """Whether the order is currently working on the order book."""
  workingTime: Timestamp
  """Millisecond timestamp the order started working on the order book."""
  origQuoteOrderQty: str
  """Original quote order quantity, as a decimal string. `0.0` when the order does not use quoteOrderQty."""
  strategyId: NotRequired[int]
  """ID labeling the order strategy this order is part of. Present only when strategyId was set on the order."""
  strategyType: NotRequired[int]
  """Type labeling the order strategy this order is part of. Present only when strategyType was set on the order."""
  selfTradePreventionMode: Literal[
    'NONE', 'EXPIRE_MAKER', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'DECREMENT', 'TRANSFER'
  ]
  """Self-trade prevention mode applied to this order."""
  preventedMatchId: NotRequired[int]
  """ID of a prevented match. Present only if the order expired due to self-trade prevention."""
  preventedQuantity: NotRequired[str]
  """Order quantity that expired due to self-trade prevention, as a decimal string. Present only if the order expired due to self-trade prevention."""


class OpenOrdersStatus(WsRpcEndpoint):
  """Current open orders"""

  async def open_orders_status(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[OrderStatus]:
    """Query execution status of all open orders. If `symbol` is omitted, open orders for all symbols are returned as a flat list.

    Args:
      symbol: Symbol to query. If omitted, open orders for all symbols are returned.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#current-open-orders-user_data)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    _Response = list[OrderStatus]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'openOrders.status', params=params, validator=_validator, validate=validate
    )
