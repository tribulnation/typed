from typing_extensions import TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class EnableFuturesItem(TypedDict):
  """Sub-account futures enablement record."""
  subAccount: str
  """Sub-account name."""
  isFuturesEnabled: bool
  """Whether futures capability was enabled."""
  timestamp: str
  """Response time, milliseconds since epoch."""

class EnableFuturesResponse(TypedDict):
  """Sub-account futures enablement response."""
  code: str
  """Result code as a string; `"0"` on success."""
  message: str
  """Status message; empty on success."""
  data: list[EnableFuturesItem]
  """Enablement result, one record per requested sub-account."""

Response: type[EnableFuturesResponse | ErrorResponse] = EnableFuturesResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class EnableFutures(AuthSpotMixin):
  async def enable_futures(
    self, *,
    sub_account: str, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> EnableFuturesResponse:
    """Enables futures trading capability for a sub-account.

    Args:
      sub_account: Sub-account name to enable futures for.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#sub-account-endpoints)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if sub_account is not None:
      params['subAccount'] = sub_account
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('POST', '/api/v3/sub-account/futures', params=params)
    return self.output(r.text, adapter, validate)
