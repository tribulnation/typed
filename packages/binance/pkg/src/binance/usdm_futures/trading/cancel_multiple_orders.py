from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BatchOrderError(TypedDict):
  """Per-element failure returned in place of an order when a batch element is rejected."""

  code: int
  """Binance error code for this element."""
  msg: str
  """Human-readable error message for this element."""


class CanceledFuturesOrder(TypedDict):
  """One successfully canceled order."""

  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""
  cumQty: str
  """Cumulative filled quantity."""
  executedQty: str
  """Cumulative filled quantity."""
  orderId: int
  """Order id."""
  origQty: str
  """Original order quantity."""
  price: str
  """Order price."""
  reduceOnly: bool
  """Whether the order only reduces an existing position."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  positionSide: Literal['BOTH', 'LONG', 'SHORT']
  """Position side."""
  status: str
  """Order status."""
  stopPrice: str
  """Trigger price for a conditional order. Ignored for LIMIT and MARKET orders."""
  closePosition: bool
  """Whether the order closes the entire position (Close-All)."""
  symbol: str
  """Trading symbol."""
  timeInForce: Literal['GTC', 'IOC', 'FOK', 'GTX', 'GTD', 'RPI']
  """Time in force."""
  origType: Literal[
    'LIMIT',
    'MARKET',
    'STOP',
    'STOP_MARKET',
    'TAKE_PROFIT',
    'TAKE_PROFIT_MARKET',
    'TRAILING_STOP_MARKET',
  ]
  """Order type at creation, unaffected by later amendments."""
  type: Literal[
    'LIMIT',
    'MARKET',
    'STOP',
    'STOP_MARKET',
    'TAKE_PROFIT',
    'TAKE_PROFIT_MARKET',
    'TRAILING_STOP_MARKET',
  ]
  """Order type."""
  activatePrice: NotRequired[str]
  """Activation price. Only returned for TRAILING_STOP_MARKET orders."""
  priceRate: NotRequired[str]
  """Callback rate. Only returned for TRAILING_STOP_MARKET orders."""
  updateTime: Timestamp
  """Time the order was last updated."""
  workingType: Literal['MARK_PRICE', 'CONTRACT_PRICE']
  """Price type used to trigger conditional orders."""
  priceProtect: bool
  """Whether price protection is active for a conditional order's trigger."""
  priceMatch: Literal[
    'OPPONENT',
    'OPPONENT_5',
    'OPPONENT_10',
    'OPPONENT_20',
    'QUEUE',
    'QUEUE_5',
    'QUEUE_10',
    'QUEUE_20',
  ]
  """Price match mode used to auto-align the order price to the order book."""
  selfTradePreventionMode: Literal[
    'NONE', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'EXPIRE_MAKER'
  ]
  """Self-trade prevention mode."""
  goodTillDate: int
  """Auto-cancel time for a GTD order, as a Unix epoch in milliseconds."""


class CancelMultipleOrders(RpcEndpoint):
  """Cancel multiple orders in one request."""

  async def cancel_multiple_orders(
    self,
    *,
    symbol: str,
    order_id_list: str | None = None,
    orig_client_order_id_list: str | None = None,
    validate: bool | None = None,
  ) -> list[CanceledFuturesOrder | BatchOrderError]:
    """Cancel multiple orders in one request.

    Args:
      symbol: Trading symbol.
      order_id_list: JSON-encoded array of order ids to cancel, e.g. '[1, 2, 3]'. Either orderIdList or origClientOrderIdList must be sent. Max 10 orders.
      orig_client_order_id_list: JSON-encoded array of client order ids to cancel, e.g. '["my_id_1","my_id_2"]'. Either orderIdList or origClientOrderIdList must be sent. Max 10 orders.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#cancel-multiple-orders)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_id_list is not None:
      params['orderIdList'] = order_id_list
    if orig_client_order_id_list is not None:
      params['origClientOrderIdList'] = orig_client_order_id_list
    _Response = list[CanceledFuturesOrder | BatchOrderError]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.authed_request(
      'DELETE',
      '/fapi/v1/batchOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
