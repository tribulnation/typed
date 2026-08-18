from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class ModifiedFuturesOrder(TypedDict):
  """The modified order."""

  orderId: int
  """Order id."""
  symbol: str
  """Trading symbol."""
  pair: str
  """Underlying contract pair."""
  status: str
  """Order status."""
  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""
  modifyId: NotRequired[int]
  """Caller-supplied modification id, echoed back when provided in the request."""
  price: str
  """Order price."""
  origQty: str
  """Original order quantity."""
  executedQty: str
  """Cumulative filled quantity."""
  cumQty: str
  """Cumulative filled quantity."""
  timeInForce: Literal['GTC', 'IOC', 'FOK', 'GTX', 'GTD', 'RPI']
  """Time in force."""
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
  reduceOnly: bool
  """Whether the order only reduces an existing position."""
  closePosition: bool
  """Whether the order closes the entire position (Close-All)."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  positionSide: Literal['BOTH', 'LONG', 'SHORT']
  """Position side."""
  stopPrice: str
  """Trigger price for a conditional order. Ignored for LIMIT and MARKET orders."""
  workingType: Literal['MARK_PRICE', 'CONTRACT_PRICE']
  """Price type used to trigger conditional orders."""
  priceProtect: bool
  """Whether price protection is active for a conditional order's trigger."""
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
  updateTime: Timestamp
  """Time the order was last updated."""


class ModifyOrder(RpcEndpoint):
  """Order modify function. Currently only LIMIT order modification is supported; a modified order is reordered in the match queue."""

  async def modify_order(
    self,
    *,
    symbol: str,
    side: Literal['BUY', 'SELL'],
    quantity: str,
    price: str,
    order_id: int | None = None,
    orig_client_order_id: str | None = None,
    price_match: Literal[
      'OPPONENT',
      'OPPONENT_5',
      'OPPONENT_10',
      'OPPONENT_20',
      'QUEUE',
      'QUEUE_5',
      'QUEUE_10',
      'QUEUE_20',
    ]
    | None = None,
    modify_id: int | None = None,
    validate: bool | None = None,
  ) -> ModifiedFuturesOrder:
    """Order modify function. Currently only LIMIT order modification is supported; a modified order is reordered in the match queue.

    Args:
      symbol: Trading symbol.
      side: Order side.
      quantity: Order quantity. Cannot be sent with closePosition=true.
      price: Order price.
      order_id: Id of the order to modify. Either orderId or origClientOrderId must be sent; orderId prevails if both are sent.
      orig_client_order_id: Client order id of the order to modify. Either orderId or origClientOrderId must be sent.
      price_match: Price match mode, auto-aligning the order price to the order book. Only available for LIMIT/STOP/TAKE_PROFIT orders; cannot be sent together with price.
      modify_id: Caller-supplied modification id, returned as-is in the response. Not validated for uniqueness.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#modify-order)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'quantity': quantity,
      'price': price,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    if price_match is not None:
      params['priceMatch'] = price_match
    if modify_id is not None:
      params['modifyId'] = modify_id
    _Response = ModifiedFuturesOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'PUT', '/fapi/v1/order', params=params, validator=_validator, validate=validate
    )
