from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class TestFuturesOrderResult(TypedDict):
  """The simulated order result."""

  clientOrderId: NotRequired[str]
  """Client order id, either caller-supplied or venue-generated."""
  cumQty: NotRequired[str]
  """Cumulative filled quantity."""
  cumQuote: NotRequired[str]
  """Cumulative quote asset transacted quantity."""
  executedQty: NotRequired[str]
  """Cumulative filled quantity."""
  orderId: NotRequired[int]
  """Order id."""
  avgPrice: NotRequired[str]
  """Average fill price."""
  origQty: NotRequired[str]
  """Original order quantity."""
  price: NotRequired[str]
  """Order price."""
  reduceOnly: NotRequired[bool]
  """Whether the order only reduces an existing position."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Order side."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """Position side."""
  status: NotRequired[str]
  """Order status."""
  stopPrice: NotRequired[str]
  """Trigger price for a conditional order. Ignored for LIMIT and MARKET orders."""
  closePosition: NotRequired[bool]
  """Whether the order closes the entire position (Close-All)."""
  symbol: NotRequired[str]
  """Trading symbol."""
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'GTX', 'GTD', 'RPI']]
  """Time in force."""
  type: NotRequired[
    Literal[
      'LIMIT',
      'MARKET',
      'STOP',
      'STOP_MARKET',
      'TAKE_PROFIT',
      'TAKE_PROFIT_MARKET',
      'TRAILING_STOP_MARKET',
    ]
  ]
  """Order type."""
  origType: NotRequired[
    Literal[
      'LIMIT',
      'MARKET',
      'STOP',
      'STOP_MARKET',
      'TAKE_PROFIT',
      'TAKE_PROFIT_MARKET',
      'TRAILING_STOP_MARKET',
    ]
  ]
  """Order type at creation, unaffected by later amendments."""
  activatePrice: NotRequired[str]
  """Activation price. Only returned for TRAILING_STOP_MARKET orders."""
  priceRate: NotRequired[str]
  """Callback rate. Only returned for TRAILING_STOP_MARKET orders."""
  updateTime: NotRequired[Timestamp]
  """Time the order was last updated."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """Price type used to trigger conditional orders."""
  priceProtect: NotRequired[bool]
  """Whether price protection is active for a conditional order's trigger."""
  priceMatch: NotRequired[
    Literal[
      'OPPONENT',
      'OPPONENT_5',
      'OPPONENT_10',
      'OPPONENT_20',
      'QUEUE',
      'QUEUE_5',
      'QUEUE_10',
      'QUEUE_20',
    ]
  ]
  """Price match mode used to auto-align the order price to the order book."""
  selfTradePreventionMode: NotRequired[
    Literal['NONE', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'EXPIRE_MAKER']
  ]
  """Self-trade prevention mode."""
  goodTillDate: NotRequired[int]
  """Auto-cancel time for a GTD order, as a Unix epoch in milliseconds."""


class TestOrder(RpcEndpoint):
  """Testing order request; this order will not be submitted to the matching engine."""

  async def test_order(
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
    reduce_only: bool | None = None,
    quantity: str | None = None,
    price: str | None = None,
    new_client_order_id: str | None = None,
    stop_price: str | None = None,
    close_position: bool | None = None,
    activation_price: str | None = None,
    callback_rate: str | None = None,
    time_in_force: Literal['GTC', 'IOC', 'FOK', 'GTX', 'GTD', 'RPI'] | None = None,
    working_type: Literal['MARK_PRICE', 'CONTRACT_PRICE'] | None = None,
    price_protect: bool | None = None,
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
  ) -> TestFuturesOrderResult:
    """Testing order request; this order will not be submitted to the matching engine.

    Args:
      symbol: Trading symbol.
      side: Order side.
      type: Order type.
      position_side: Position side. Defaults to BOTH for One-way Mode; must be sent as LONG or SHORT in Hedge Mode.
      reduce_only: Whether the order only reduces an existing position. Cannot be sent in Hedge Mode; cannot be sent with closePosition=true.
      quantity: Order quantity. Cannot be sent with closePosition=true.
      price: Order price.
      new_client_order_id: Caller-supplied id for the order. Automatically generated if not sent. Must match ^[.A-Z:/a-z0-9_-]{1,36}$.
      stop_price: Trigger price. Used with STOP/STOP_MARKET or TAKE_PROFIT/TAKE_PROFIT_MARKET orders.
      close_position: Close-All. Used with STOP_MARKET or TAKE_PROFIT_MARKET orders.
      activation_price: Activation price for a TRAILING_STOP_MARKET order. Defaults to the latest price (supporting different workingType).
      callback_rate: Callback rate for a TRAILING_STOP_MARKET order.
      time_in_force: Time in force.
      working_type: Price type used to trigger conditional orders.
      price_protect: Whether price protection is active for a conditional order's trigger.
      new_order_resp_type: Response shape to return.
      price_match: Price match mode, auto-aligning the order price to the order book. Only available for LIMIT/STOP/TAKE_PROFIT orders; cannot be sent together with price.
      self_trade_prevention_mode: Self-trade prevention mode. Only effective when timeInForce is IOC, GTC or GTD.
      good_till_date: Order auto-cancel time for timeInForce GTD, as a Unix epoch in milliseconds. Mandatory when timeInForce is GTD.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#test-order)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'type': type,
    }
    if position_side is not None:
      params['positionSide'] = position_side
    if reduce_only is not None:
      params['reduceOnly'] = reduce_only
    if quantity is not None:
      params['quantity'] = quantity
    if price is not None:
      params['price'] = price
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    if stop_price is not None:
      params['stopPrice'] = stop_price
    if close_position is not None:
      params['closePosition'] = close_position
    if activation_price is not None:
      params['activationPrice'] = activation_price
    if callback_rate is not None:
      params['callbackRate'] = callback_rate
    if time_in_force is not None:
      params['timeInForce'] = time_in_force
    if working_type is not None:
      params['workingType'] = working_type
    if price_protect is not None:
      params['priceProtect'] = price_protect
    if new_order_resp_type is not None:
      params['newOrderRespType'] = new_order_resp_type
    if price_match is not None:
      params['priceMatch'] = price_match
    if self_trade_prevention_mode is not None:
      params['selfTradePreventionMode'] = self_trade_prevention_mode
    if good_till_date is not None:
      params['goodTillDate'] = good_till_date
    _Response = TestFuturesOrderResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/fapi/v1/order/test',
      params=params,
      validator=_validator,
      validate=validate,
    )
