"""`POST /api/v1/position/risk-limit-level/change` — Modify Isolated Margin Risk Limit."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class ModifyIsolatedMarginRiskLimitParams(TypedDict):
  """Symbol and target risk-limit level."""

  symbol: str
  """Symbol of the contract, e.g. `XBTUSDTM`."""
  level: int
  """Risk-limit level to switch to (see Get Isolated Margin Risk Limit for the available levels and their leverage/margin-rate tiers)."""


_Type = bool
adapter = validator[_Type](_Type)  # type: ignore


class ModifyIsolatedMarginRiskLimit(RpcEndpoint):
  """`Modify Isolated Margin Risk Limit` — mixed into `Positions`, the product exposing `futures.positions.modify_isolated_margin_risk_limit`."""

  async def modify_isolated_margin_risk_limit(
    self,
    modify_isolated_margin_risk_limit_params: ModifyIsolatedMarginRiskLimitParams,
    *,
    validate: bool | None = None,
  ) -> bool:
    """Change the isolated-margin risk-limit level for an existing position. Adjusting the level cancels any open orders on the symbol.

    Args:
      modify_isolated_margin_risk_limit_params: Symbol and target risk-limit level.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/position/risk-limit-level/change',
      json=modify_isolated_margin_risk_limit_params,
      validator=adapter,
      validate=validate,
    )
