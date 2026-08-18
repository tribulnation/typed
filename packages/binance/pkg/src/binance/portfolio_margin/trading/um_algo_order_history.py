from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmUmAlgoOrderHistory(TypedDict):
  """PmUmAlgoOrderHistory."""

  algoId: NotRequired[int]
  """algoId."""
  clientAlgoId: NotRequired[str]
  """clientAlgoId."""
  algoType: NotRequired[str]
  """algoType."""
  orderType: NotRequired[str]
  """orderType."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """positionSide."""
  timeInForce: NotRequired[str]
  """timeInForce."""
  algoStatus: NotRequired[str]
  """algoStatus."""
  actualOrderId: NotRequired[str]
  """actualOrderId."""
  actualPrice: NotRequired[str]
  """actualPrice."""
  triggerPrice: NotRequired[str]
  """triggerPrice."""
  workingType: NotRequired[Literal['MARK_PRICE', 'CONTRACT_PRICE']]
  """workingType."""
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
  """priceMatch."""
  closePosition: NotRequired[bool]
  """closePosition."""
  priceProtect: NotRequired[bool]
  """priceProtect."""
  reduceOnly: NotRequired[bool]
  """reduceOnly."""
  createTime: NotRequired[Timestamp]
  """createTime."""
  updateTime: NotRequired[Timestamp]
  """updateTime."""
  triggerTime: NotRequired[Timestamp]
  """triggerTime."""
  goodTillDate: NotRequired[int]
  """goodTillDate."""


class UmAlgoOrderHistory(RpcEndpoint):
  """Query UM Algo Order History"""

  async def um_algo_order_history(
    self,
    *,
    symbol: str,
    algo_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[PmUmAlgoOrderHistory]:
    """Get all algo orders: ACTIVE, CANCELED, TRIGGERED or FINISHED.

    Args:
      symbol: Trading pair symbol.
      algo_id: Only return orders >= this algoId.
      start_time: Lower bound of the query window, inclusive.
      end_time: Upper bound of the query window, inclusive.
      limit: Default 500; max 1000.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-um-algo-order-history)
    """
    params: dict = {
      'symbol': symbol,
    }
    if algo_id is not None:
      params['algoId'] = algo_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[PmUmAlgoOrderHistory]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/um/algo/allAlgoOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
