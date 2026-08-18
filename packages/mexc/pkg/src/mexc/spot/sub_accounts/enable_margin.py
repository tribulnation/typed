from typing_extensions import TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class EnableMarginItem(TypedDict):
  """Sub-account margin enablement record."""
  subAccount: str
  """Sub-account name."""
  isMarginEnabled: bool
  """Whether margin capability was enabled."""
  timestamp: str
  """Response time, milliseconds since epoch."""

class EnableMarginResponse(TypedDict):
  """Sub-account margin enablement response."""
  code: str
  """Result code as a string; `"0"` on success."""
  message: str
  """Status message; empty on success."""
  data: list[EnableMarginItem]
  """Enablement result, one record per requested sub-account."""

Response: type[EnableMarginResponse | ErrorResponse] = EnableMarginResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class EnableMargin(AuthSpotMixin):
  async def enable_margin(
    self, *,
    sub_account: str, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> EnableMarginResponse:
    """Enables margin trading capability for a sub-account.

    Args:
      sub_account: Sub-account name to enable margin for.
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
    r = await self.signed_request('POST', '/api/v3/sub-account/margin', params=params)
    return self.output(r.text, adapter, validate)
