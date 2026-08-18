from typing_extensions import Literal, NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.futures.core import AuthFuturesMixin

class BatchQueryItem(TypedDict):
  """Futures order record."""
  orderId: int | str
  """Order identifier."""
  symbol: str
  """Contract symbol."""
  positionId: int | str
  """Related position identifier."""
  price: float
  """Order or trigger price."""
  vol: float
  """Order volume."""
  leverage: int
  """Leverage used by the order."""
  side: Literal[1, 2, 3, 4]
  """Order side: 1 open long, 2 close short, 3 open short, 4 close long."""
  category: Literal[1, 2, 3, 4]
  """Order category: 1 limit order, 2 system take-over delegate, 3 close delegate, 4 ADL reduction."""
  orderType: Literal[1, 2, 3, 4, 5, 6]
  """Order type: 1 limit, 2 post-only maker, 3 IOC, 4 FOK, 5 market, 6 market-to-current-price."""
  dealAvgPrice: float
  """Average filled price."""
  dealVol: float
  """Filled volume."""
  orderMargin: float
  """Margin reserved for the order."""
  takerFee: float
  """Taker fee."""
  makerFee: float
  """Maker fee."""
  profit: float
  """Realized close profit."""
  feeCurrency: str
  """Fee currency."""
  openType: Literal[1, 2]
  """Margin mode: 1 isolated, 2 cross."""
  state: Literal[1, 2, 3, 4, 5]
  """Order state: 1 uninformed, 2 uncompleted, 3 completed, 4 cancelled, 5 invalid."""
  externalOid: str
  """Client-provided external order id."""
  errorCode: int
  """Order error code."""
  usedMargin: float
  """Used margin."""
  createTime: Timestamp | Timestamp
  """Creation time."""
  updateTime: Timestamp | Timestamp
  """Last update time."""
  stopLossPrice: NotRequired[float]
  """Attached stop-loss price when present."""
  takeProfitPrice: NotRequired[float]
  """Attached take-profit price when present."""

class BatchQueryResponse(TypedDict):
  """Batch query futures orders by id response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[BatchQueryItem]]
  """Batch order query results."""

adapter = validator(BatchQueryResponse)

class BatchQuery(AuthFuturesMixin):
  async def batch_query(
    self, *,
    order_ids: str, validate: bool | None = None,
  ) -> BatchQueryResponse:
    """Returns multiple futures orders for a comma-separated list of order ids.

    Args:
      order_ids: Comma-separated order ids; maximum 50 ids.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#query-the-order-in-bulk-based-on-the-order-number)
    """
    headers = {}
    params = {}
    if order_ids is not None:
      params['order_ids'] = order_ids
    r = await self.signed_request('GET', '/api/v1/private/order/batch_query', params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)
