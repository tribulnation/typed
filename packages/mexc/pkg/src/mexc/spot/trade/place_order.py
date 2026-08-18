from typing_extensions import Literal, NotRequired, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class PlaceOrderResponse(TypedDict):
  """Created order response."""
  symbol: str
  """Spot symbol."""
  orderId: int | str
  """MEXC order id."""
  orderListId: int | str
  """Order-list id."""
  clientOrderId: NotRequired[str | None]
  """Client order id."""
  price: str
  """Price."""
  origQty: str
  """Original quantity."""
  executedQty: NotRequired[str]
  """Executed quantity."""
  cummulativeQuoteQty: NotRequired[str]
  """Executed quote quantity."""
  status: NotRequired[Literal['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'PARTIALLY_CANCELED']]
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
  transactTime: Timestamp
  """transactTime timestamp in milliseconds."""

Response: type[PlaceOrderResponse | ErrorResponse] = PlaceOrderResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class PlaceOrder(AuthSpotMixin):
  async def place_order(
    self, *,
    symbol: str, side: Literal['BUY', 'SELL'],
    type_: Literal['LIMIT', 'MARKET', 'LIMIT_MAKER', 'IMMEDIATE_OR_CANCEL', 'FILL_OR_KILL'],
    quantity: str | None = None, quote_order_qty: str | None = None,
    price: str | None = None, new_client_order_id: str | None = None,
    recv_window: int | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> PlaceOrderResponse:
    """Creates a live spot order on the signed account.

    Args:
      symbol: Spot symbol.
      side: Order side.
      type_: Order type.
      quantity: Base-asset quantity.
      quote_order_qty: Quote-asset amount.
      price: Limit price.
      new_client_order_id: Client order id.
      recv_window: Optional receive window in milliseconds; maximum 60000.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#new-order)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if side is not None:
      params['side'] = side
    if type_ is not None:
      params['type'] = type_
    if quantity is not None:
      params['quantity'] = quantity
    if quote_order_qty is not None:
      params['quoteOrderQty'] = quote_order_qty
    if price is not None:
      params['price'] = price
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    if recv_window is not None:
      params['recvWindow'] = recv_window
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('POST', '/api/v3/order', params=params)
    return self.output(r.text, adapter, validate)
