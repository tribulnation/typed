from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginAssetRiskBasedLiquidationRatio(TypedDict):
  """Risk-based liquidation ratio for one margin asset."""

  asset: str
  """Margin asset symbol, e.g. USDC."""
  riskBasedLiquidationRatio: str
  """Fraction of a position liquidated in one step under risk-based liquidation, as a decimal string."""


class RiskBasedLiquidationRatio(RpcEndpoint):
  """Get Margin Asset Risk-Based Liquidation Ratio"""

  async def risk_based_liquidation_ratio(
    self,
    *,
    validate: bool | None = None,
  ) -> list[MarginAssetRiskBasedLiquidationRatio]:
    """Query the risk-based liquidation ratio applied to each margin asset -- the fraction of a position liquidated in one step under risk-based liquidation.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#get-margin-asset-risk-based-liquidation-ratio)
    """
    _Response = list[MarginAssetRiskBasedLiquidationRatio]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/sapi/v1/margin/risk-based-liquidation-ratio',
      validator=_validator,
      validate=validate,
    )
