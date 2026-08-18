from typing_extensions import TypedDict
from mexc.spot.core import ErrorResponse, SpotMixin
from mexc.core import validator

class DefaultSymbolsResponse(TypedDict):
  code: int
  """API status code."""
  data: list[str]
  """Default spot symbols."""
  msg: str | None
  """API message, often null."""

Response: type[DefaultSymbolsResponse | ErrorResponse] = DefaultSymbolsResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class DefaultSymbols(SpotMixin):
  async def default_symbols(
    self, *,
    validate: bool | None = None,
  ) -> DefaultSymbolsResponse:
    """Return MEXC spot default symbols.

    Args:
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#api-default-symbol)
    """
    params = {}
    r = await self.request('GET', '/api/v3/defaultSymbols')
    return self.output(r.text, adapter, validate)
