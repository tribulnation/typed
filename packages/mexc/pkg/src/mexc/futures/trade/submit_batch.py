from typing_extensions import Literal, NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class SubmitBatchDataItem(TypedDict):
  """Per-order batch placement result."""
  externalOid: str
  """Client-supplied external order identifier."""
  orderId: int | str | None
  """Created order identifier when placement succeeds."""
  errorMsg: str | None
  """Error message when placement fails."""
  errorCode: int
  """Placement result code; zero indicates success."""

class SubmitBatchRequestItem(TypedDict):
  """Single batch order request."""
  symbol: str
  """Contract symbol, for example BTC_USDT."""
  price: float
  """Order price. Market-price orders may ignore or use venue-specific handling."""
  vol: float
  """Order volume in contracts."""
  leverage: NotRequired[int]
  """Leverage to use; required for isolated margin according to the docs."""
  side: Literal[1, 2, 3, 4]
  """Order direction: 1 open long, 2 close short, 3 open short, 4 close long."""
  type: Literal[1, 2, 3, 4, 5, 6]
  """Order type: 1 limit, 2 post-only maker, 3 IOC, 4 FOK, 5 market, 6 market-to-current-price."""
  openType: Literal[1, 2]
  """Margin mode: 1 isolated, 2 cross."""
  positionId: NotRequired[int]
  """Position identifier, recommended when closing a position."""
  externalOid: NotRequired[str]
  """Client-supplied external order identifier."""
  stopLossPrice: NotRequired[float]
  """Stop-loss price attached to the order."""
  takeProfitPrice: NotRequired[float]
  """Take-profit price attached to the order."""

class SubmitBatchResponse(TypedDict):
  """Futures batch order response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[SubmitBatchDataItem]]
  """Per-order placement results."""

adapter = validator(SubmitBatchResponse)

class SubmitBatch(AuthFuturesMixin):
  async def submit_batch(
    self, list_submit_batch_request_item: list[SubmitBatchRequestItem], *,
    validate: bool | None = None,
  ) -> SubmitBatchResponse:
    """Places up to 50 futures orders in one request when the endpoint and account permission are available.

    Args:
      list_submit_batch_request_item: Request parameter.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#bulk-order-under-maintenance)
    """
    params = {}
    r = await self.signed_post('/api/v1/private/order/submit_batch', json=list_submit_batch_request_item)
    return self.envelope_output(r.text, adapter, validate)
