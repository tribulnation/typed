from typing_extensions import NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class CancelAllStopRequest(TypedDict):
  """Cancel all futures stop-limit trigger orders request body."""
  positionId: NotRequired[int]
  """Position identifier to scope cancellation."""
  symbol: NotRequired[str]
  """Contract symbol to scope cancellation; omit with positionId to cancel all stop-limit trigger orders."""

class CancelAllStopResponse(TypedDict):
  """Futures write endpoint response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""

adapter = validator(CancelAllStopResponse)

class CancelAllStop(AuthFuturesMixin):
  async def cancel_all_stop(
    self, cancel_all_stop_request: CancelAllStopRequest, *,
    validate: bool | None = None,
  ) -> CancelAllStopResponse:
    """Cancels stop-limit trigger orders by position, by symbol, or across all symbols when no scope is provided.

    Args:
      cancel_all_stop_request: Request parameter.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#cancel-all-stop-limit-price-trigger-orders-under-maintenance)
    """
    params = {}
    r = await self.signed_post('/api/v1/private/stoporder/cancel_all', json=cancel_all_stop_request)
    return self.envelope_output(r.text, adapter, validate)
