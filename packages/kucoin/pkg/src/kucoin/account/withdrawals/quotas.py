"""`GET /api/v1/withdrawals/quotas` — Get Withdrawal Quotas."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class WithdrawalQuota(TypedDict):
  """Withdrawal quota, limits and fee info for one currency."""

  currency: str
  """Currency."""
  limitBTCAmount: str
  """Daily withdrawal limit expressed in BTC."""
  usedBTCAmount: str
  """Amount already withdrawn today, expressed in BTC."""
  quotaCurrency: str
  """Currency the withdrawal limit fields below are denominated in."""
  limitQuotaCurrencyAmount: str
  """Daily withdrawal limit, denominated in `quotaCurrency`."""
  usedQuotaCurrencyAmount: str
  """Amount already withdrawn today, denominated in `quotaCurrency`."""
  remainAmount: str
  """Remaining amount available to withdraw today, in `currency`."""
  availableAmount: str
  """Currently available account balance for `currency` that could be withdrawn."""
  withdrawMinFee: str
  """Minimum fee charged for an on-chain withdrawal of `currency`."""
  innerWithdrawMinFee: str
  """Minimum fee charged for an internal (KuCoin-to-KuCoin) withdrawal of `currency`."""
  withdrawMinSize: str
  """Minimum withdrawal amount for `currency`."""
  isWithdrawEnabled: bool
  """Whether withdrawals of `currency` are currently enabled."""
  precision: int
  """Decimal precision for `currency` withdrawal amounts."""
  chain: str
  """Chain name the quota applies to, e.g. `BTC`, `TRC20`, `ARBITRUM` -- note this is the chain *name*, a different value space from the `chain` request parameter's chain *id* (e.g. `trx` in the request comes back as `TRC20` here)."""
  reason: str | None
  """Reason withdrawals are restricted, if `isWithdrawEnabled` is false; `null` when not restricted."""
  lockedAmount: str
  """Total amount currently locked (e.g. pending withdrawals), including amounts locked in other currencies converted into this one."""


_Type = WithdrawalQuota
adapter = validator[_Type](_Type)  # type: ignore


class Quotas(RpcEndpoint):
  """`Get Withdrawal Quotas` — mixed into `Withdrawals`, the product exposing `account.withdrawals.quotas`."""

  async def quotas(
    self,
    *,
    currency: str,
    chain: str | None = None,
    validate: bool | None = None,
  ) -> WithdrawalQuota:
    """Get the authenticated account's withdrawal quota information for one currency -- daily/remaining limits, minimum size and fee, and whether withdrawals are currently enabled for it.

    Args:
      currency: Currency to get withdrawal quota info for, e.g. `BTC`, `ETH`, `USDT`.
      chain: Chain id of the currency, needed only for a multi-chain currency (single-chain currencies ignore it). E.g. for USDT: `omni`, `erc20`, `trc20`; for BTC: `btc`, `bech32`, `trx`. Defaults to `eth`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'currency': currency,
    }
    if chain is not None:
      params['chain'] = chain
    return await self.authed_request(
      'GET',
      '/api/v1/withdrawals/quotas',
      params=params,
      validator=adapter,
      validate=validate,
    )
