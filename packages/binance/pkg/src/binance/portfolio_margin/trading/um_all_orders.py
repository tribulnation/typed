from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmAllCurrentUmOpenOrders(TypedDict):
  """PmAllCurrentUmOpenOrders."""

  avgPrice: NotRequired[str]
  """Avg Price."""
  clientOrderId: NotRequired[str]
  """Client Order ID."""
  cumQuote: NotRequired[str]
  """Cum Quote."""
  executedQty: NotRequired[str]
  """Executed Qty."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  origQty: NotRequired[str]
  """Orig Qty."""
  origType: NotRequired[str]
  """Orig Type."""
  price: NotRequired[str]
  """Price."""
  reduceOnly: NotRequired[bool]
  """Reduce Only."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Side."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """BOTH means that it is the position of One-way Mode."""
  status: NotRequired[str]
  """Enum：completed，processing."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  time: NotRequired[Timestamp]
  """order time."""
  timeInForce: NotRequired[str]
  """Time In Force."""
  type: NotRequired[str]
  """Normal order type after trigger if appliable."""
  updateTime: NotRequired[Timestamp]
  """update time."""
  selfTradePreventionMode: NotRequired[str]
  """self trading preventation mode."""
  goodTillDate: NotRequired[int]
  """order pre-set auot cancel time for TIF GTD order."""
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


class UmAllOrders(RpcEndpoint):
  """Query All UM Orders"""

  async def um_all_orders(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[PmAllCurrentUmOpenOrders]:
    """Get all account UM orders; active, canceled, or filled.

    Args:
      symbol: Symbol.
      order_id: Order id to act on.
      start_time: Timestamp in ms to get funding from INCLUSIVE.
      end_time: Timestamp in ms to get funding until INCLUSIVE.
      limit: Number of results returned.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-all-um-orders)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[PmAllCurrentUmOpenOrders]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/um/allOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
