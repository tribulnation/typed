from typing_extensions import TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class ReferCodeResponse(TypedDict):
  """Referral code response."""
  referCode: str
  """Referral code for the signed account."""

Response: type[ReferCodeResponse | ErrorResponse] = ReferCodeResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class ReferCode(AuthSpotMixin):
  async def refer_code(
    self, *,
    recv_window: int | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> ReferCodeResponse:
    """Returns the referral code associated with the signed account.

    Args:
      recv_window: Optional receive window in milliseconds.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-refercode)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if recv_window is not None:
      params['recvWindow'] = recv_window
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/rebate/referCode', params=params)
    return self.output(r.text, adapter, validate)
