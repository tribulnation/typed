"""`GET /api/v1/contracts/risk-limit/{symbol}` — Get Isolated Margin Risk Limit."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class IsolatedRiskLimitLevel(TypedDict):
  """One isolated-margin risk-limit tier for a contract."""

  symbol: str
  """Symbol of the contract."""
  level: int
  """Risk-limit level."""
  maxRiskLimit: int
  """Upper position-value limit for this level (inclusive), in the settlement currency."""
  minRiskLimit: int
  """Lower position-value limit for this level, in the settlement currency."""
  maxLeverage: int
  """Maximum leverage allowed at this level."""
  initialMargin: float
  """Initial margin rate at this level."""
  maintainMargin: float
  """Maintenance margin rate at this level."""


_Type = list[IsolatedRiskLimitLevel]
adapter = validator[_Type](_Type)  # type: ignore


class GetIsolatedMarginRiskLimit(RpcEndpoint):
  """`Get Isolated Margin Risk Limit` — mixed into `Positions`, the product exposing `futures.positions.get_isolated_margin_risk_limit`."""

  async def get_isolated_margin_risk_limit(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> list[IsolatedRiskLimitLevel]:
    """Get the isolated-margin risk-limit ladder for a contract: the leverage/margin-rate tiers a position size falls into. Only valid for isolated margin.

    Args:
      symbol: Symbol of the contract, e.g. `XBTUSDTM`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.request(
      'GET',
      f'/api/v1/contracts/risk-limit/{symbol}',
      validator=adapter,
      validate=validate,
    )
