from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMNewOrderResult(TypedDict):
  """The newly-created order."""

  clientOrderId: NotRequired[str]
  """Client order ID."""
  cumQty: NotRequired[str]
  """Cumulative filled quantity, in contracts."""
  executedQty: NotRequired[str]
  """Executed quantity, in contracts."""
  orderId: int
  """Order ID."""
  origQty: NotRequired[str]
  """Original order quantity, in contracts."""
  price: NotRequired[str]
  """Order price."""
  reduceOnly: NotRequired[bool]
  """Whether the order is reduce-only."""
  closePosition: NotRequired[bool]
  """Whether the order closes the whole position (Close-All)."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """Position side."""
  status: Literal['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'EXPIRED']
  """Order status. Documented closed set (COIN-M common-definition doc)."""
  stopPrice: NotRequired[str]
  """Stop trigger price. Ignored when order type is TRAILING_STOP_MARKET."""
  symbol: str
  """Symbol."""
  pair: NotRequired[str]
  """Underlying pair."""
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'GTX']]
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
  """Order type. See `notes` — after the CM/UM migration this endpoint rejects the five stop-type values with -4120; only LIMIT and MARKET are currently accepted here."""
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
  """Original order type."""
  activatePrice: NotRequired[str]
  """Activation price. Only returned for TRAILING_STOP_MARKET orders."""
  priceRate: NotRequired[str]
  """Callback rate. Only returned for TRAILING_STOP_MARKET orders."""
  updateTime: NotRequired[int]
  """Last update time."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """stopPrice trigger price type."""
  priceProtect: NotRequired[bool]
  """Whether the conditional order's trigger is price-protected."""
  priceMatch: NotRequired[str]
  """Price match mode."""
  selfTradePreventionMode: NotRequired[str]
  """Self-trade prevention mode."""


class NewOrder(RpcEndpoint):
  """New Order"""

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
    reduce_only: Literal['true', 'false'] | None = None,
    quantity: float | None = None,
    price: float | None = None,
    new_client_order_id: str | None = None,
    stop_price: float | None = None,
    close_position: Literal['true', 'false'] | None = None,
    activation_price: float | None = None,
    callback_rate: float | None = None,
    time_in_force: Literal['GTC', 'IOC', 'FOK', 'GTX'] | None = None,
    working_type: Literal['MARK_PRICE', 'CONTRACT_PRICE'] | None = None,
    price_protect: Literal['true', 'false'] | None = None,
    new_order_resp_type: Literal['ACK', 'RESULT'] | None = None,
    price_match: Literal[
      'NONE',
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
    validate: bool | None = None,
  ) -> CoinMNewOrderResult:
    """Send in a new order.

    Args:
      symbol: Symbol, e.g. BTCUSD_PERP.
      side: Order side.
      type: Order type. See `notes` — after the CM/UM migration this endpoint rejects the five stop-type values with -4120; only LIMIT and MARKET are currently accepted here.
      position_side: Position side. `BOTH` for One-way Mode; `LONG` or `SHORT` for Hedge Mode.
      reduce_only: Whether the order is reduce-only. Cannot be sent in Hedge Mode; cannot be sent together with `closePosition=true`.
      quantity: Order quantity, in contracts. Cannot be sent together with `closePosition=true`.
      price: Order price.
      new_client_order_id: A unique id among open orders. Auto-generated if not sent. Must match `^[.A-Z:/a-z0-9_-]{1,36}$`.
      stop_price: Trigger price. Used with STOP/STOP_MARKET or TAKE_PROFIT/TAKE_PROFIT_MARKET orders.
      close_position: Close-All: closes the whole position. Used with STOP_MARKET or TAKE_PROFIT_MARKET orders. Cannot be sent together with `quantity` or `reduceOnly`.
      activation_price: Used with TRAILING_STOP_MARKET orders; defaults to the latest price.
      callback_rate: Callback rate, used with TRAILING_STOP_MARKET orders. Min 0.1, max 10, where 1 means 1%.
      time_in_force: Time in force.
      working_type: stopPrice trigger price type.
      price_protect: Whether the conditional order's trigger is price-protected. Used with STOP/STOP_MARKET or TAKE_PROFIT/TAKE_PROFIT_MARKET orders.
      new_order_resp_type: Response verbosity.
      price_match: Price match mode. Only available for LIMIT/STOP/TAKE_PROFIT orders; cannot be sent together with `price`.
      self_trade_prevention_mode: Self-trade prevention mode. Only effective when `timeInForce` is IOC or GTC.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#new-order)
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
    _Response = CoinMNewOrderResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST', '/dapi/v1/order', params=params, validator=_validator, validate=validate
    )
