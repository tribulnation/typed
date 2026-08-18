from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class MultiAssetCollateralRequest(TypedDict):
  """Request to change a portfolio's Multi Asset Collateral setting."""

  portfolio_uuid: str
  """The portfolio UUID."""
  multi_asset_collateral_enabled: bool
  """Enable or disable Multi Asset Collateral."""


class MultiAssetCollateralResponse(TypedDict):
  """Result of changing the Multi Asset Collateral setting."""

  multi_asset_collateral_enabled: bool
  """Whether Multi Asset Collateral is now enabled for the portfolio."""


@dataclass(frozen=True, kw_only=True)
class MultiAssetCollateral(RpcEndpoint):
  """`POST /api/v3/brokerage/intx/multi_asset_collateral`."""

  async def __call__(
    self,
    multi_asset_collateral_request: MultiAssetCollateralRequest,
  ) -> MultiAssetCollateralResponse:
    """Opt a perpetuals portfolio in or out of Multi Asset Collateral on Coinbase International Exchange (INTX). Deprecated: this INTX perpetuals surface retires 2026-09-09, replaced by a Deribit-powered derivatives gateway (see `upstream.md`).

    Args:
      multi_asset_collateral_request: The portfolio to change and the desired setting.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/perpetuals/opt-in-or-out)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/brokerage/intx/multi_asset_collateral',
      json=multi_asset_collateral_request,
      validator=validator(MultiAssetCollateralResponse),
    )
