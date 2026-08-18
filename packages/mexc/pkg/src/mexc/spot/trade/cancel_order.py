from typing_extensions import Literal, NotRequired, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class CancelOrderResponse(TypedDict):
  """Canceled order response."""
  symbol: str
  """Spot symbol."""
  orderId: int | str
  """MEXC order id."""
  orderListId: NotRequired[int | str]
  """Order-list id."""
  clientOrderId: NotRequired[str | None]
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
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK']]
  """Time in force."""
  type: Literal['LIMIT', 'MARKET', 'LIMIT_MAKER', 'IMMEDIATE_OR_CANCEL', 'FILL_OR_KILL']
  """Order type."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  time: NotRequired[Timestamp]
  """Creation time."""
  updateTime: NotRequired[Timestamp]
  """Update time."""
  isWorking: NotRequired[bool]
  """Whether active on the order book."""
  origClientOrderId: NotRequired[str]
  """origClientOrderId identifier."""

Response: type[CancelOrderResponse | ErrorResponse] = CancelOrderResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class CancelOrder(AuthSpotMixin):
  async def cancel_order(
    self, *,
    symbol: str, order_id: str | None = None,
    orig_client_order_id: str | None = None,
    new_client_order_id: str | None = None, recv_window: int | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> CancelOrderResponse:
    """Cancels one active spot order by order id or original client order id.

    Args:
      symbol: Spot symbol.
      order_id: Order id.
      orig_client_order_id: Original client order id.
      new_client_order_id: Optional cancel client id.
      recv_window: Optional receive window in milliseconds; maximum 60000.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-order)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if order_id is not None:
      params['orderId'] = order_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    if recv_window is not None:
      params['recvWindow'] = recv_window
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('DELETE', '/api/v3/order', params=params)
    return self.output(r.text, adapter, validate)
