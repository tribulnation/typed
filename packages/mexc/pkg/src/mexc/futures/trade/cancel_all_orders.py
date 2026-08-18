from typing_extensions import NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class CancelAllOrdersRequest(TypedDict):
  """Cancel all futures orders request body."""
  symbol: NotRequired[str]
  """Contract symbol to scope cancellation; omit to cancel all uncompleted orders."""

class CancelAllOrdersResponse(TypedDict):
  """Futures write endpoint response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""

adapter = validator(CancelAllOrdersResponse)

class CancelAllOrders(AuthFuturesMixin):
  async def cancel_all_orders(
    self, cancel_all_orders_request: CancelAllOrdersRequest, *,
    validate: bool | None = None,
  ) -> CancelAllOrdersResponse:
    """Cancels all uncompleted futures orders, optionally scoped to one contract symbol.

    Args:
      cancel_all_orders_request: Request parameter.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#cancel-all-orders-under-a-contract-under-maintenance)
    """
    params = {}
    r = await self.signed_post('/api/v1/private/order/cancel_all', json=cancel_all_orders_request)
    return self.envelope_output(r.text, adapter, validate)
