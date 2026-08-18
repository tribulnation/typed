"""`spot.account.balance_ex` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class ExtendedBalance(TypedDict):
  """Extended balance detail for one asset."""

  balance: NotRequired[str]
  """Total balance amount for this asset."""
  credit: NotRequired[str]
  """Total credit amount. Only present if the account has a credit line."""
  credit_used: NotRequired[str]
  """Used credit amount. Only present if the account has a credit line."""
  hold_trade: NotRequired[str]
  """Total held amount for this asset (spot non-margin orders only)."""


validate_balance_ex = validator(dict[str, ExtendedBalance])


class BalanceEx(RpcEndpoint):
  """`spot.account.balance_ex`."""

  async def balance_ex(
    self,
    rebase_multiplier: Literal['rebased', 'base'] | None = None,
  ) -> dict[str, ExtendedBalance]:
    """Retrieve all extended account balances, including credit and held amounts. Balance available for trading is `balance + credit - credit_used - hold_trade`. Held amounts only include spot non-margin orders.

    **Note on Staking/Earn assets:** assets migrated from the legacy Staking system to the new Earn system may appear with symbol extensions -- `.B`, `.F`, `.S`, `.M`, `.T` -- these are read-only for transacting; use the base asset instead.

    **API Key Permissions Required:** `Funds permissions - Query`

    Args:
      rebase_multiplier: Optional parameter for viewing xstocks data. `rebased` displays in terms of underlying equity, `base` displays in terms of SPV tokens.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/get-extended-balance)
    """
    data = {}
    if rebase_multiplier is not None:
      data['rebase_multiplier'] = rebase_multiplier

    return await self.authed_request(
      '/0/private/BalanceEx', data, validator=validate_balance_ex
    )
