from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import Literal, TypedDict
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class OrderStatus(TypedDict):
  """Order status."""
  symbol: str
  """Spot symbol."""
  orderId: int | str
  """MEXC order id."""
  orderListId: int
  """Order-list id."""
  clientOrderId: str | None
  """Client order id."""
  price: str
  """Price."""
  origQty: str
  """Original quantity."""
  executedQty: str
  """Executed quantity."""
  cummulativeQuoteQty: str
  """Executed quote quantity."""
  status: Literal['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'PARTIALLY_CANCELED']
  """Order status."""
  timeInForce: Literal['GTC', 'IOC', 'FOK']
  """Time in force."""
  type: Literal['LIMIT', 'MARKET', 'LIMIT_MAKER', 'IMMEDIATE_OR_CANCEL', 'FILL_OR_KILL']
  """Order type."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  stopPrice: str
  """Stop price."""
  icebergQty: str
  """Iceberg quantity."""
  time: Timestamp
  """Creation time."""
  updateTime: Timestamp
  """Update time."""
  isWorking: bool
  """Whether active on the order book."""
  origQuoteOrderQty: str
  """Original quote order quantity."""

Response: type[list[OrderStatus] | ErrorResponse] = list[OrderStatus] | ErrorResponse # type: ignore
adapter = validator(Response)

class Orders(AuthSpotMixin):
  async def orders(
    self, *,
    symbol: str, start_time: Timestamp | None = None,
    end_time: Timestamp | None = None, limit: int | None = None,
    recv_window: int | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> list[OrderStatus]:
    """Returns active, canceled, and completed orders for a symbol in a bounded time window.

    Args:
      symbol: Spot symbol.
      start_time: Window start time in milliseconds.
      end_time: Window end time in milliseconds.
      limit: Default 500; maximum 1000.
      recv_window: Optional receive window in milliseconds; maximum 60000.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#all-orders)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if start_time is not None:
      params['startTime'] = ts.dump(start_time)
    if end_time is not None:
      params['endTime'] = ts.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    if recv_window is not None:
      params['recvWindow'] = recv_window
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/allOrders', params=params)
    return self.output(r.text, adapter, validate)
