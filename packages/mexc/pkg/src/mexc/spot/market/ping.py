from typing_extensions import TypedDict
from mexc.spot.core import ErrorResponse, SpotMixin
from mexc.core import validator

class PingResponse(TypedDict):
  """Empty successful connectivity response."""

Response: type[PingResponse | ErrorResponse] = PingResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class Ping(SpotMixin):
  async def ping(self, *, validate: bool | None = None) -> PingResponse:
    """Test connectivity to the MEXC spot REST API.

    Args:
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#test-connectivity)
    """
    params = {}
    r = await self.request('GET', '/api/v3/ping')
    return self.output(r.text, adapter, validate)
