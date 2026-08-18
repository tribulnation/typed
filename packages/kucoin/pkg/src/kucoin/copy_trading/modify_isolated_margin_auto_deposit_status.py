"""`POST /api/v1/copy-trade/futures/position/margin/auto-deposit-status` — Modify Isolated Margin Auto-Deposit Status."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class ModifyCopyTradeIsolatedMarginAutoDepositStatusParams(TypedDict):
  """Symbol, position side and target auto-deposit status."""

  symbol: str
  """Contract symbol, e.g. `XBTUSDTM`."""
  status: bool
  """Enable (`true`) or disable (`false`) automatic margin deposit."""
  positionSide: Literal['LONG', 'SHORT']
  """Position side."""


_Type = bool
adapter = validator[_Type](_Type)  # type: ignore


class ModifyIsolatedMarginAutoDepositStatus(RpcEndpoint):
  """`Modify Isolated Margin Auto-Deposit Status` — mixed into `CopyTrading`, the product exposing `copy_trading.modify_isolated_margin_auto_deposit_status`."""

  async def modify_isolated_margin_auto_deposit_status(
    self,
    modify_copy_trade_isolated_margin_auto_deposit_status_params: ModifyCopyTradeIsolatedMarginAutoDepositStatusParams,
    *,
    validate: bool | None = None,
  ) -> bool:
    """Enable or disable automatic margin deposit (to avoid liquidation) for an existing copy-trading isolated position. The docs page notes this feature "is no longer recommended" and suggests using cross margin instead. Requires the API key's `LeadtradeFutures` permission.

    Args:
      modify_copy_trade_isolated_margin_auto_deposit_status_params: Symbol, position side and target auto-deposit status.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/copy-trade/futures/position/margin/auto-deposit-status',
      json=modify_copy_trade_isolated_margin_auto_deposit_status_params,
      validator=adapter,
      validate=validate,
    )
