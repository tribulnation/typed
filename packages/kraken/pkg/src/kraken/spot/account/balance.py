"""`spot.account.balance` -- private Spot endpoint."""

from typing_extensions import Literal
from typed_core.validation import validator
from ...core.endpoint.rpc import RpcEndpoint


validate_balance = validator(dict[str, str])


class Balance(RpcEndpoint):
  """`spot.account.balance`."""

  async def balance(
    self,
    rebase_multiplier: Literal['rebased', 'base'] | None = None,
  ) -> dict[str, str]:
    """Retrieve all cash balances, net of pending withdrawals.

    **Note on Staking/Earn assets:** assets migrated from the legacy Staking system to the new Earn system may appear in balances and ledgers with symbol extensions -- `.B` (new yield-bearing products), `.F` (auto-earning Kraken Rewards), `.S`/`.M` (legacy staked/opt-in-reward balances), `.T` (tokenized assets). These are read-only for transacting; use the base asset (e.g. `USDT`) instead.

    **API Key Permissions Required:** `Funds permissions - Query`

    Args:
      rebase_multiplier: Optional parameter for viewing xstocks data. `rebased` displays in terms of underlying equity, `base` displays in terms of SPV tokens.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/get-account-balance)
    """
    data = {}
    if rebase_multiplier is not None:
      data['rebase_multiplier'] = rebase_multiplier

    return await self.authed_request(
      '/0/private/Balance', data, validator=validate_balance
    )
