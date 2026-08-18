from typing_extensions import Literal, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class TestOrderResponse(TypedDict):
  """Empty response when validation succeeds."""

Response: type[TestOrderResponse | ErrorResponse] = TestOrderResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class TestOrder(AuthSpotMixin):
  async def test_order(
    self, *,
    symbol: str, side: Literal['BUY', 'SELL'],
    type_: Literal['LIMIT', 'MARKET', 'LIMIT_MAKER', 'IMMEDIATE_OR_CANCEL', 'FILL_OR_KILL'],
    quantity: str | None = None, quote_order_qty: str | None = None,
    price: str | None = None, new_client_order_id: str | None = None,
    recv_window: int | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> TestOrderResponse:
    """Validates a new order without sending it to the matching engine.

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
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#test-new-order)
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
    r = await self.signed_request('POST', '/api/v3/order/test', params=params)
    return self.output(r.text, adapter, validate)
