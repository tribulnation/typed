from typing_extensions import TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class SelfSymbolsResponse(TypedDict):
  """Default symbol wrapper."""
  code: int
  """Response code."""
  data: list[str]
  """Enabled symbols."""
  msg: str | None
  """Message."""

Response: type[SelfSymbolsResponse | ErrorResponse] = SelfSymbolsResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class SelfSymbols(AuthSpotMixin):
  async def self_symbols(
    self, *,
    recv_window: int | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> SelfSymbolsResponse:
    """Returns the symbols enabled for the signed API key.

    Args:
      recv_window: Optional receive window in milliseconds; maximum 60000.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#user-api-default-symbol)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if recv_window is not None:
      params['recvWindow'] = recv_window
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/selfSymbols', params=params)
    return self.output(r.text, adapter, validate)
