from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class NewFuturesOrder(TypedDict):
  """The created order."""

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


class NewOrder(RpcEndpoint):
  """Send in a new order. Additional parameters become mandatory depending on type: LIMIT requires timeInForce, quantity and price; MARKET requires quantity."""

  async def new_order(
    self,
    *,
    symbol: str,
    side: Literal['BUY', 'SELL'],
    type: Literal[
      'LIMIT',
      'MARKET',
      'STOP',
      'STOP_MARKET',
      'TAKE_PROFIT',
      'TAKE_PROFIT_MARKET',
      'TRAILING_STOP_MARKET',
    ],
    position_side: Literal['BOTH', 'LONG', 'SHORT'] | None = None,
    time_in_force: Literal['GTC', 'IOC', 'FOK', 'GTX', 'GTD', 'RPI'] | None = None,
    reduce_only: bool | None = None,
    quantity: str | None = None,
    price: str | None = None,
    new_client_order_id: str | None = None,
    new_order_resp_type: Literal['ACK', 'RESULT'] | None = None,
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
    self_trade_prevention_mode: Literal[
      'NONE', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'EXPIRE_MAKER'
    ]
    | None = None,
    good_till_date: int | None = None,
    validate: bool | None = None,
  ) -> NewFuturesOrder:
    """Send in a new order. Additional parameters become mandatory depending on type: LIMIT requires timeInForce, quantity and price; MARKET requires quantity.

    Args:
      symbol: Trading symbol.
      side: Order side.
      type: Order type.
      position_side: Position side. Defaults to BOTH for One-way Mode; must be sent as LONG or SHORT in Hedge Mode.
      time_in_force: Time in force. Required for LIMIT orders.
      reduce_only: Whether the order only reduces an existing position. Cannot be sent in Hedge Mode.
      quantity: Order quantity. Required for LIMIT and MARKET orders.
      price: Order price. Required for LIMIT orders.
      new_client_order_id: Caller-supplied id for the order. Automatically generated if not sent. Must match ^[.A-Z:/a-z0-9_-]{1,36}$.
      new_order_resp_type: Response shape to return.
      price_match: Price match mode, auto-aligning the order price to the order book. Only available for LIMIT/STOP/TAKE_PROFIT orders; cannot be sent together with price.
      self_trade_prevention_mode: Self-trade prevention mode. Only effective when timeInForce is IOC, GTC or GTD.
      good_till_date: Order auto-cancel time for timeInForce GTD, as a Unix epoch in milliseconds. Mandatory when timeInForce is GTD; retains only second-level precision; must be greater than the current time plus 600 seconds and smaller than 253402300799000.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#new-order)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'type': type,
    }
    if position_side is not None:
      params['positionSide'] = position_side
    if time_in_force is not None:
      params['timeInForce'] = time_in_force
    if reduce_only is not None:
      params['reduceOnly'] = reduce_only
    if quantity is not None:
      params['quantity'] = quantity
    if price is not None:
      params['price'] = price
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    if new_order_resp_type is not None:
      params['newOrderRespType'] = new_order_resp_type
    if price_match is not None:
      params['priceMatch'] = price_match
    if self_trade_prevention_mode is not None:
      params['selfTradePreventionMode'] = self_trade_prevention_mode
    if good_till_date is not None:
      params['goodTillDate'] = good_till_date
    _Response = NewFuturesOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST', '/fapi/v1/order', params=params, validator=_validator, validate=validate
    )
