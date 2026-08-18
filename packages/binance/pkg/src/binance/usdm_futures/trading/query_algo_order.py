from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FuturesAlgoOrderStatus(TypedDict):
  """USD-M Futures algo (conditional) order status."""

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
  actualType: NotRequired[str]
  """Actual order type placed once triggered."""
  actualQty: NotRequired[str]
  """Actual executed quantity of the triggered order."""
  triggerPrice: NotRequired[str]
  """Trigger price."""
  icebergQuantity: NotRequired[str]
  """Iceberg quantity."""
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


class QueryAlgoOrder(RpcEndpoint):
  """Check the status of an algo (conditional) order, such as TP/SL (Take Profit / Stop Loss) or trailing stop orders on USD-M Futures. Either algoId or clientAlgoId must be sent. Orders are not found once CANCELED/EXPIRED with no filled trade and created more than 3 days ago, or created more than 90 days ago."""

  async def query_algo_order(
    self,
    *,
    algo_id: int | None = None,
    client_algo_id: str | None = None,
    validate: bool | None = None,
  ) -> FuturesAlgoOrderStatus:
    """Check the status of an algo (conditional) order, such as TP/SL (Take Profit / Stop Loss) or trailing stop orders on USD-M Futures. Either algoId or clientAlgoId must be sent. Orders are not found once CANCELED/EXPIRED with no filled trade and created more than 3 days ago, or created more than 90 days ago.

    Args:
      algo_id: Algo order ID. Self-increments per symbol. Either this or clientAlgoId is required.
      client_algo_id: Client algo order ID. Either this or algoId is required.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#query-algo-order)
    """
    params = {}
    if algo_id is not None:
      params['algoId'] = algo_id
    if client_algo_id is not None:
      params['clientAlgoId'] = client_algo_id
    _Response = FuturesAlgoOrderStatus
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/fapi/v1/algoOrder',
      params=params,
      validator=_validator,
      validate=validate,
    )
