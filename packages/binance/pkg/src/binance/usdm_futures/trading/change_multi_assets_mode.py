from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class ChangeMultiAssetsModeResult(TypedDict):
  """Result of changing the account's Multi-Assets mode."""

  code: int
  """Result code."""
  msg: NotRequired[str]
  """Result message."""


class ChangeMultiAssetsMode(RpcEndpoint):
  """Change user's Multi-Assets mode (Multi-Assets Mode or Single-Asset Mode) on every symbol."""

  async def change_multi_assets_mode(
    self,
    *,
    multi_assets_margin: bool,
    validate: bool | None = None,
  ) -> ChangeMultiAssetsModeResult:
    """Change user's Multi-Assets mode (Multi-Assets Mode or Single-Asset Mode) on every symbol.

    Args:
      multi_assets_margin: true: Multi-Assets Mode; false: Single-Asset Mode.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#change-multi-assets-mode)
    """
    params: dict = {
      'multiAssetsMargin': multi_assets_margin,
    }
    _Response = ChangeMultiAssetsModeResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/fapi/v1/multiAssetsMargin',
      params=params,
      validator=_validator,
      validate=validate,
    )
