from typing_extensions import TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class ConvertibleAssetsItem(TypedDict):
  """Convertible asset."""
  convertMx: str | None
  """Estimated MX amount after fee."""
  convertUsdt: str | None
  """Estimated USDT amount."""
  balance: str | None
  """Convertible balance."""
  asset: str | None
  """Asset."""
  code: str | None
  """Per-asset code."""
  message: str | None
  """Per-asset message."""

Response: type[list[ConvertibleAssetsItem] | ErrorResponse] = list[ConvertibleAssetsItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class ConvertibleAssets(AuthSpotMixin):
  async def convertible_assets(
    self, *,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> list[ConvertibleAssetsItem]:
    """Returns dust balances and estimated MX/USDT conversion values for assets that can be converted.

    Args:
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-assets-that-can-be-converted-into-mx)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/capital/convert/list', params=params)
    return self.output(r.text, adapter, validate)
