from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SpotOrder(TypedDict):
  """A spot order, in the shape returned by order-query endpoints."""

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
  icebergQty: str
  """Iceberg order quantity, as a decimal string. `0.0` when not an iceberg order."""
  time: int
  """Millisecond timestamp the order was created."""
  updateTime: int
  """Millisecond timestamp the order was last updated."""
  isWorking: bool
  """Whether the order is currently working on the order book."""
  origQuoteOrderQty: str
  """Original quote order quantity, as a decimal string."""
  workingTime: int
  """Millisecond timestamp the order started working on the order book."""
  selfTradePreventionMode: Literal[
    'NONE', 'EXPIRE_MAKER', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'DECREMENT', 'TRANSFER'
  ]
  """Self-trade prevention mode applied to this order."""


class Order(RpcEndpoint):
  """Query order"""

  async def order(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    orig_client_order_id: str | None = None,
    validate: bool | None = None,
  ) -> SpotOrder:
    """Check an order's status. Either `orderId` or `origClientOrderId` must be sent. If both are provided, `orderId` is searched first, then `origClientOrderId` is checked against that result; the request is rejected if neither condition is met.

    Args:
      symbol: Symbol the order was placed on.
      order_id: Order ID to query. Either `orderId` or `origClientOrderId` is required.
      orig_client_order_id: Client order ID to query. Either `orderId` or `origClientOrderId` is required.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    _Response = SpotOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/api/v3/order', params=params, validator=_validator, validate=validate
    )
