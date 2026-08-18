from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMTestOrderResult(TypedDict):
  """Empty object on success — the order is validated but never sent to the matching engine."""


class OrderTest(RpcEndpoint):
  """Test Order"""

  async def order_test(
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
  ) -> CoinMTestOrderResult:
    """Validate a new order's parameters without sending it to the matching engine. Same request shape as `new_order`.

    Args:
      symbol: Symbol, e.g. BTCUSD_PERP.
      side: Order side.
      type: Order type. See `notes` — after the CM/UM migration this endpoint rejects the five stop-type values with -4120; only LIMIT and MARKET are currently accepted here.
      position_side: Position side. `BOTH` for One-way Mode; `LONG` or `SHORT` for Hedge Mode.
      reduce_only: Whether the order is reduce-only. Cannot be sent in Hedge Mode; cannot be sent together with `closePosition=true`.
      quantity: Order quantity, in contracts. Cannot be sent together with `closePosition=true`.
      price: Order price.
      new_client_order_id: A unique id among open orders. Auto-generated if not sent.
      stop_price: Trigger price. Used with STOP/STOP_MARKET or TAKE_PROFIT/TAKE_PROFIT_MARKET orders.
      close_position: Close-All. Used with STOP_MARKET or TAKE_PROFIT_MARKET orders.
      activation_price: Used with TRAILING_STOP_MARKET orders.
      callback_rate: Callback rate for TRAILING_STOP_MARKET orders.
      time_in_force: Time in force.
      working_type: stopPrice trigger price type.
      price_protect: Whether the conditional order's trigger is price-protected.
      new_order_resp_type: Response verbosity.
      price_match: Price match mode. Only available for LIMIT/STOP/TAKE_PROFIT orders; cannot be sent together with `price`.
      self_trade_prevention_mode: Self-trade prevention mode. Only effective when `timeInForce` is IOC or GTC.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#test-order)
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
    _Response = CoinMTestOrderResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/dapi/v1/order/test',
      params=params,
      validator=_validator,
      validate=validate,
    )
