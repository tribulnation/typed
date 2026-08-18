from typing_extensions import Any, Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class SubAccountMarginSummaryCrossMarginSummary(TypedDict):
  """Cross-margin-only summary for this subaccount."""

  accountValue: str
  """Total account value, as a decimal string."""
  totalNtlPos: str
  """Total notional position size, as a decimal string."""
  totalRawUsd: str
  """Total raw USD value of positions, as a decimal string."""
  totalMarginUsed: str
  """Total margin currently used, as a decimal string."""


class SubAccountMarginSummaryMarginSummary(TypedDict):
  """Isolated + cross margin summary for this subaccount."""

  accountValue: str
  """Total account value, as a decimal string."""
  totalNtlPos: str
  """Total notional position size, as a decimal string."""
  totalRawUsd: str
  """Total raw USD value of positions, as a decimal string."""
  totalMarginUsed: str
  """Total margin currently used, as a decimal string."""


class SubAccountSpotBalance(TypedDict):
  """Spot balance for one coin in this subaccount."""

  coin: str
  """Spot coin symbol."""
  token: int
  """Spot token index."""
  total: str
  """Total balance, as a decimal string."""
  hold: str
  """Portion of the balance currently held by open orders, as a decimal string."""
  entryNtl: str
  """Entry notional value of the held balance, as a decimal string."""


class SubAccountsAction(TypedDict):
  type: Literal['subAccounts']
  user: str


class SubAccountClearinghouseState(TypedDict):
  """Perpetuals clearinghouse state for this subaccount (same shape as `info.clearinghouse_state`)."""

  marginSummary: SubAccountMarginSummaryMarginSummary
  crossMarginSummary: SubAccountMarginSummaryCrossMarginSummary
  crossMaintenanceMarginUsed: str
  """Cross-margin maintenance margin currently used, as a decimal string."""
  withdrawable: str
  """Amount withdrawable from this subaccount, as a decimal string."""
  assetPositions: list[dict[str, Any]]
  """Open perpetual positions for this subaccount. Always empty in captured examples."""
  time: int
  """State snapshot time, in milliseconds since epoch."""


class SubAccountSpotState(TypedDict):
  """Spot account state for this subaccount (same shape as `info.spot_clearinghouse_state`)."""

  balances: list[SubAccountSpotBalance]
  """Spot balances held by this subaccount."""


class SubAccount(TypedDict):
  """One subaccount belonging to the queried master account."""

  name: str
  """Subaccount display name, as set by the master account. Not a fixed set of values."""
  subAccountUser: str
  """The subaccount's own address."""
  master: str
  """Address of the master account that owns this subaccount."""
  clearinghouseState: SubAccountClearinghouseState
  spotState: SubAccountSpotState


adapter = pydantic.TypeAdapter(list[SubAccount] | None)


class SubAccounts(InfoMixin):
  async def sub_accounts(self, *, user: str) -> list[SubAccount] | None:
    """Retrieve the subaccounts belonging to a master account, including each subaccount's perpetuals clearinghouse state and spot balances.

    Args:
      user: Address to look up, as a 42-character hexadecimal string.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: SubAccountsAction = {
      'type': 'subAccounts',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
