from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmCancelCmConditionalOrder(TypedDict):
  """Cancel CM Conditional Order."""

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
  timeInForce: NotRequired[str]
  """Time In Force."""
  activatePrice: NotRequired[str]
  """activation price, only return with TRAILING_STOP_MARKET order."""
  priceRate: NotRequired[str]
  """callback rate, only return with TRAILING_STOP_MARKET order."""
  bookTime: NotRequired[Timestamp]
  """order place time."""
  updateTime: NotRequired[Timestamp]
  """last update time."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """Working Type."""
  priceProtect: NotRequired[bool]
  """Price Protect."""


class CancelCmConditionalOrder(RpcEndpoint):
  """Cancel CM Conditional Order"""

  async def cancel_cm_conditional_order(
    self,
    *,
    symbol: str,
    strategy_id: int | None = None,
    new_client_strategy_id: str | None = None,
    validate: bool | None = None,
  ) -> PmCancelCmConditionalOrder:
    """Cancel CM Conditional Order.

    Args:
      symbol: Symbol.
      strategy_id: Conditional order strategy id to act on.
      new_client_strategy_id: Caller-supplied id for the new conditional order. Automatically generated if not sent.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#cancel-cm-conditional-order)
    """
    params: dict = {
      'symbol': symbol,
    }
    if strategy_id is not None:
      params['strategyId'] = strategy_id
    if new_client_strategy_id is not None:
      params['newClientStrategyId'] = new_client_strategy_id
    _Response = PmCancelCmConditionalOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/papi/v1/cm/conditional/order',
      params=params,
      validator=_validator,
      validate=validate,
    )
