from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FuturesAlgoOrderRecord(TypedDict):
  """A USD-M Futures algo (conditional) order record."""

  algoId: int
  """Algo order ID."""
  clientAlgoId: NotRequired[str]
  """Client algo order ID."""
  algoType: Literal['CONDITIONAL']
  """Algo order family."""
  orderType: Literal[
    'LIMIT',
    'MARKET',
    'STOP',
    'STOP_MARKET',
    'TAKE_PROFIT',
    'TAKE_PROFIT_MARKET',
    'TRAILING_STOP_MARKET',
  ]
  """Underlying order type."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """Position side."""
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'GTX', 'GTD', 'RPI']]
  """Time in force."""
  algoStatus: NotRequired[str]
  """Algo order status. Left bare (not enum) — see notes."""
  actualOrderId: NotRequired[str]
  """The real order ID this algo order triggered, once fired."""
  actualPrice: NotRequired[str]
  """Actual execution price of the triggered order."""
  triggerPrice: NotRequired[str]
  """Trigger price."""
  icebergQuantity: NotRequired[str]
  """Iceberg quantity."""
  tpTriggerPrice: NotRequired[str]
  """Take-profit trigger price, for TP/SL algo orders."""
  tpPrice: NotRequired[str]
  """Take-profit price, for TP/SL algo orders."""
  slTriggerPrice: NotRequired[str]
  """Stop-loss trigger price, for TP/SL algo orders."""
  slPrice: NotRequired[str]
  """Stop-loss price, for TP/SL algo orders."""
  tpOrderType: NotRequired[str]
  """Take-profit order type, if applicable."""
  selfTradePreventionMode: NotRequired[
    Literal['NONE', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'EXPIRE_MAKER']
  ]
  """Self-trade prevention mode."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """Price type used to evaluate the trigger condition."""
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
  """Auto price-match mode."""
  closePosition: NotRequired[bool]
  """Whether this is a Close-All order."""
  priceProtect: NotRequired[bool]
  """Whether price protection is enabled."""
  reduceOnly: NotRequired[bool]
  """Whether the order is reduce-only."""
  createTime: NotRequired[int]
  """Algo order creation time, milliseconds since epoch."""
  updateTime: NotRequired[int]
  """Last update time, milliseconds since epoch."""
  triggerTime: NotRequired[int]
  """Time the order was triggered, milliseconds since epoch."""
  goodTillDate: NotRequired[int]
  """Auto-cancel time for timeInForce GTD, milliseconds since epoch."""


class AllAlgoOrders(RpcEndpoint):
  """Get all algo (conditional) orders — active, CANCELED, TRIGGERED, or FINISHED — including TP/SL (Take Profit / Stop Loss) and trailing stop orders on USD-M Futures. If algoId is set, returns orders >= that algoId; otherwise the most recent orders are returned. The query time period must be less than 7 days (defaults to the most recent 7 days)."""

  async def all_algo_orders(
    self,
    *,
    symbol: str,
    algo_id: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[FuturesAlgoOrderRecord]:
    """Get all algo (conditional) orders — active, CANCELED, TRIGGERED, or FINISHED — including TP/SL (Take Profit / Stop Loss) and trailing stop orders on USD-M Futures. If algoId is set, returns orders >= that algoId; otherwise the most recent orders are returned. The query time period must be less than 7 days (defaults to the most recent 7 days).

    Args:
      symbol: Trading symbol, e.g. BTCUSDT.
      algo_id: If set, returns orders with algoId >= this value.
      start_time: Start time, milliseconds since epoch.
      end_time: End time, milliseconds since epoch.
      limit: Max number of rows to return.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#query-all-algo-orders)
    """
    params: dict = {
      'symbol': symbol,
    }
    if algo_id is not None:
      params['algoId'] = algo_id
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    _Response = list[FuturesAlgoOrderRecord]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/fapi/v1/allAlgoOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
