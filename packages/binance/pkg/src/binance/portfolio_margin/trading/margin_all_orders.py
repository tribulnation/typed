from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmAllMarginAccountOrders(TypedDict):
  """PmAllMarginAccountOrders."""

  clientOrderId: NotRequired[str]
  """Client Order ID."""
  cummulativeQuoteQty: NotRequired[str]
  """Cummulative Quote Qty."""
  executedQty: NotRequired[str]
  """Executed Qty."""
  icebergQty: NotRequired[str]
  """Iceberg Qty."""
  isWorking: NotRequired[bool]
  """Is Working."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  origQty: NotRequired[str]
  """Orig Qty."""
  price: NotRequired[str]
  """Price."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Side."""
  status: NotRequired[str]
  """Enum：completed，processing."""
  stopPrice: NotRequired[str]
  """please ignore when order type is TRAILING_STOP_MARKET."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  time: NotRequired[Timestamp]
  """Event time."""
  timeInForce: NotRequired[str]
  """Time In Force."""
  type: NotRequired[str]
  """Normal order type after trigger if appliable."""
  updateTime: NotRequired[Timestamp]
  """last update time."""
  accountId: NotRequired[int]
  """Account ID."""
  selfTradePreventionMode: NotRequired[str]
  """self trading preventation mode."""
  preventedMatchId: NotRequired[str]
  """Prevented Match ID."""
  preventedQuantity: NotRequired[str]
  """Prevented Quantity."""


class MarginAllOrders(RpcEndpoint):
  """Query All Margin Account Orders"""

  async def margin_all_orders(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[PmAllMarginAccountOrders]:
    """Query All Margin Account Orders.

    Args:
      symbol: Symbol.
      order_id: Order id to act on.
      start_time: Timestamp in ms to get funding from INCLUSIVE.
      end_time: Timestamp in ms to get funding until INCLUSIVE.
      limit: Number of results returned.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-all-margin-account-orders)
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
    _Response = list[PmAllMarginAccountOrders]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/margin/allOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
