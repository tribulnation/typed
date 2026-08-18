from typing_extensions import TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class MxDeductStatusData(TypedDict):
  """Response data."""
  mxDeductEnable: bool
  """Whether MX deduction is enabled."""

class MxDeductStatusResponse(TypedDict):
  """Wrapper response."""
  data: MxDeductStatusData
  code: int
  """Response code."""
  msg: str
  """Response message."""
  timestamp: Timestamp
  """Response timestamp."""

Response: type[MxDeductStatusResponse | ErrorResponse] = MxDeductStatusResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class MxDeductStatus(AuthSpotMixin):
  async def mx_deduct_status(
    self, *,
    recv_window: int | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> MxDeductStatusResponse:
    """Returns whether MX deduction for spot commission fees is enabled.

    Args:
      recv_window: Optional receive window in milliseconds; maximum 60000.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-mx-deduct-status)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if recv_window is not None:
      params['recvWindow'] = recv_window
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/mxDeduct/enable', params=params)
    return self.output(r.text, adapter, validate)
