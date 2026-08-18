from typing_extensions import TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class CancelWithdrawResponse(TypedDict):
  """Withdrawal cancellation response."""
  id: str | None
  """Canceled withdrawal id."""

Response: type[CancelWithdrawResponse | ErrorResponse] = CancelWithdrawResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class CancelWithdraw(AuthSpotMixin):
  async def cancel_withdraw(
    self, *,
    id: str, timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> CancelWithdrawResponse:
    """Cancels a pending withdrawal by withdrawal id.

    Args:
      id: Withdrawal id to cancel.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-withdraw)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if id is not None:
      params['id'] = id
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('DELETE', '/api/v3/capital/withdraw', params=params)
    return self.output(r.text, adapter, validate)
