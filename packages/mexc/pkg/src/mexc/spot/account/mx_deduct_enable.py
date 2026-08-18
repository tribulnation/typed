from typing_extensions import TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class MxDeductEnableData(TypedDict):
  """Response data."""
  mxDeductEnable: bool
  """Whether MX deduction is enabled."""

class MxDeductEnableResponse(TypedDict):
  """Wrapper response."""
  data: MxDeductEnableData
  code: int
  """Response code."""
  msg: str
  """Response message."""
  timestamp: Timestamp
  """Response timestamp."""

Response: type[MxDeductEnableResponse | ErrorResponse] = MxDeductEnableResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class MxDeductEnable(AuthSpotMixin):
  async def mx_deduct_enable(
    self, *,
    mx_deduct_enable: bool, recv_window: int | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> MxDeductEnableResponse:
    """Enables or disables MX deduction for spot commission fees.

    Args:
      mx_deduct_enable: Set true to enable MX deduction, false to disable it.
      recv_window: Optional receive window in milliseconds; maximum 60000.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#enable-mx-deduct)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if mx_deduct_enable is not None:
      params['mxDeductEnable'] = mx_deduct_enable
    if recv_window is not None:
      params['recvWindow'] = recv_window
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('POST', '/api/v3/mxDeduct/enable', params=params)
    return self.output(r.text, adapter, validate)
