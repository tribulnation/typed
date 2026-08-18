from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MultiAssetsMode(TypedDict):
  """The account's current Multi-Assets margin mode, applied across every symbol."""

  multiAssetsMargin: bool
  """true: Multi-Assets Mode; false: Single-Asset Mode."""


class MultiAssetsModeEndpoint(RpcEndpoint):
  """Get user's Multi-Assets mode (Multi-Assets Mode or Single-Asset Mode) on every symbol."""

  async def multi_assets_mode(self, *, validate: bool | None = None) -> MultiAssetsMode:
    """Get user's Multi-Assets mode (Multi-Assets Mode or Single-Asset Mode) on every symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-current-multi-assets-mode)
    """
    _Response = MultiAssetsMode
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/fapi/v1/multiAssetsMargin', validator=_validator, validate=validate
    )
