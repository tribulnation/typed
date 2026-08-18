"""`GET /v5/account/wallet-balance` — Get Wallet Balance.

Hand-written PoC predating a real `account` spec — `typed-dev codegen python bybit` will
delete this file (and `account/__init__.py`'s `Account`/`Http.account` wiring) on its next
run, since codegen clears the whole `http` output base and only knows about spec'd
endpoints. Restore both after regenerating, until `account.wallet_balance` has a real spec.
"""

from typing_extensions import Literal, NotRequired, TypedDict
from bybit.core import Endpoint, validator


class Coin(TypedDict):
  """One coin's balance within an account."""

  coin: str
  """Coin symbol, for example `USDT`."""
  equity: str
  """Equity, including unrealized PnL."""
  walletBalance: str
  """Wallet balance, excluding unrealized PnL."""
  availableToWithdraw: NotRequired[str]
  """Amount currently free to withdraw."""


class AccountBalance(TypedDict):
  """One account's balance and margin state."""

  accountType: str
  """Account type, for example `UNIFIED`."""
  totalEquity: NotRequired[str]
  """Total equity across every coin, in USD."""
  totalWalletBalance: NotRequired[str]
  """Total wallet balance across every coin, in USD."""
  coin: list[Coin]
  """Per-coin balances."""


class WalletBalanceResult(TypedDict):
  """Wallet balance response."""

  list: list[AccountBalance]


adapter = validator[WalletBalanceResult](WalletBalanceResult)


class WalletBalance(Endpoint):
  """`Get Wallet Balance` — mixed into the router that owns `account.wallet_balance`."""

  async def wallet_balance(
    self,
    *,
    accountType: Literal['UNIFIED', 'CONTRACT', 'SPOT'],
    coin: str | None = None,
    validate: bool | None = None,
  ) -> WalletBalanceResult:
    """Get the authenticated account's wallet balance and margin state.

    Args:
      accountType: Account type to query.
      coin: Restrict the response to one coin, for example `USDT`. Omit for every coin.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/account/wallet-balance)
    """
    params: dict = {'accountType': accountType}
    if coin is not None:
      params['coin'] = coin
    r = await self.authed_request('GET', '/v5/account/wallet-balance', params=params)
    return self.result(r, adapter, validate)
