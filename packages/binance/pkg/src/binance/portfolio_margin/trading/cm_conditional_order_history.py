from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmCmConditionalOrderHistory(TypedDict):
  """Query CM Conditional Order History."""

  newClientStrategyId: NotRequired[str]
  """New Client Strategy ID."""
  strategyId: NotRequired[int]
  """Strategy ID."""
  strategyStatus: NotRequired[str]
  """Strategy Status."""
  strategyType: NotRequired[
    Literal[
      'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET'
    ]
  ]
  """Strategy Type."""
  origQty: NotRequired[str]
  """Orig Qty."""
  price: NotRequired[str]
  """Price."""
  reduceOnly: NotRequired[bool]
  """Reduce Only."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Side."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """BOTH means that it is the position of One-way Mode."""
  stopPrice: NotRequired[str]
  """please ignore when order type is TRAILING_STOP_MARKET."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable，only have when the strategy is triggered."""
  status: NotRequired[str]
  """Normal order status after trigger if appliable, only have when the strategy is triggered."""
  bookTime: NotRequired[Timestamp]
  """order time."""
  updateTime: NotRequired[Timestamp]
  """last update time."""
  triggerTime: NotRequired[Timestamp]
  """Trigger Time."""
  timeInForce: NotRequired[str]
  """Time In Force."""
  type: NotRequired[str]
  """Normal order type after trigger if appliable."""
  activatePrice: NotRequired[str]
  """activation price, only return with TRAILING_STOP_MARKET order."""
  priceRate: NotRequired[str]
  """callback rate, only return with TRAILING_STOP_MARKET order."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """Working Type."""
  priceProtect: NotRequired[bool]
  """Price Protect."""
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
  """Price Match."""


class CmConditionalOrderHistory(RpcEndpoint):
  """Query CM Conditional Order History"""

  async def cm_conditional_order_history(
    self,
    *,
    symbol: str,
    strategy_id: int | None = None,
    new_client_strategy_id: str | None = None,
    validate: bool | None = None,
  ) -> PmCmConditionalOrderHistory:
    """Query CM Conditional Order History.

    Args:
      symbol: Symbol.
      strategy_id: Conditional order strategy id to act on.
      new_client_strategy_id: Caller-supplied id for the new conditional order. Automatically generated if not sent.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-cm-conditional-order-history)
    """
    params: dict = {
      'symbol': symbol,
    }
    if strategy_id is not None:
      params['strategyId'] = strategy_id
    if new_client_strategy_id is not None:
      params['newClientStrategyId'] = new_client_strategy_id
    _Response = PmCmConditionalOrderHistory
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/cm/conditional/orderHistory',
      params=params,
      validator=_validator,
      validate=validate,
    )
