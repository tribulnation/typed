"""`POST /api/v1/copy-trade/futures/position/risk-limit-level/change` — Modify Isolated Margin Risk Limit."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class ModifyCopyTradeIsolatedMarginRiskLimitParams(TypedDict):
  """Symbol and target risk-limit level."""

  symbol: str
  """Contract symbol, e.g. `XBTUSDTM`."""
  level: int
  """Risk-limit level to switch to."""


_Type = bool
adapter = validator[_Type](_Type)  # type: ignore


class ModifyIsolatedMarginRiskLimit(RpcEndpoint):
  """`Modify Isolated Margin Risk Limit` — mixed into `CopyTrading`, the product exposing `copy_trading.modify_isolated_margin_risk_limit`."""

  async def modify_isolated_margin_risk_limit(
    self,
    modify_copy_trade_isolated_margin_risk_limit_params: ModifyCopyTradeIsolatedMarginRiskLimitParams,
    *,
    validate: bool | None = None,
  ) -> bool:
    """Change the isolated-margin risk-limit level for an existing copy-trading position. Adjusting the level cancels any open orders on the symbol. Requires the API key's `LeadtradeFutures` permission.

    Args:
      modify_copy_trade_isolated_margin_risk_limit_params: Symbol and target risk-limit level.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/copy-trade/futures/position/risk-limit-level/change',
      json=modify_copy_trade_isolated_margin_risk_limit_params,
      validator=adapter,
      validate=validate,
    )
