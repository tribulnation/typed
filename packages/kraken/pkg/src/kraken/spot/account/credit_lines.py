"""`spot.account.credit_lines` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class CreditLinesAsset(TypedDict):
  """Credit line details for one asset."""

  balance: NotRequired[str]
  """Current balance for the asset."""
  hold_trade: NotRequired[str]
  """Amount on hold for open orders."""
  collateral_value: NotRequired[float]
  """Collateral value factor for this asset (present for eligible collateral assets)."""
  credit_limit: NotRequired[str]
  """Credit limit for the asset (present only for accounts with a credit line)."""
  credit_used: NotRequired[str]
  """Currently used credit for the asset (present only for accounts with a credit line)."""
  available_credit: NotRequired[str]
  """Available credit for the asset (present only for accounts with a credit line)."""


class CreditLinesMonitor(TypedDict):
  """Portfolio-wide credit summary."""

  total_credit_usd: NotRequired[str | None]
  """Aggregate credit limit across all assets, in USD."""
  total_credit_used_usd: NotRequired[str | None]
  """Aggregate utilized credit across all assets, in USD."""
  total_collateral_value_usd: NotRequired[str | None]
  """Sum of asset balances in USD times each asset's collateral factor."""
  equity_usd: NotRequired[str | None]
  """Total collateral value minus total credit used, in USD."""
  ongoing_balance: NotRequired[str | None]
  """Ratio of total collateral value to total credit, in USD."""
  debt_to_equity: NotRequired[str | None]
  """Ratio of total credit used to equity, in USD."""


class CreditLines0(TypedDict):
  asset_details: NotRequired[dict[str, CreditLinesAsset]]
  """Per-asset credit line balances, keyed by asset code."""
  limits_monitor: NotRequired[CreditLinesMonitor]


_credit_lines_type = CreditLines0 | None
validate_credit_lines = validator[_credit_lines_type](_credit_lines_type)  # type: ignore


class CreditLines(RpcEndpoint):
  """`spot.account.credit_lines`."""

  async def credit_lines(
    self,
    rebase_multiplier: Literal['rebased', 'base'] | None = None,
  ) -> CreditLines0 | None:
    """Retrieve all credit line details for VIP accounts with this functionality. Several response fields are only present for accounts with an active credit line.

    **API Key Permissions Required:** `Funds permissions - Query`

    Args:
      rebase_multiplier: Optional parameter for viewing xstocks data. `rebased` displays in terms of underlying equity, `base` displays in terms of SPV tokens.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/get-credit-lines)
    """
    data = {}
    if rebase_multiplier is not None:
      data['rebase_multiplier'] = rebase_multiplier

    return await self.authed_request(
      '/0/private/CreditLines', data, validator=validate_credit_lines
    )
