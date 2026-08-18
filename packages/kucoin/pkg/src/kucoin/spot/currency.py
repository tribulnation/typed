"""`GET /api/v3/currencies/{currency}` — Get Currency."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class CurrencyChain(TypedDict):
  """Deposit/withdrawal parameters for one blockchain network."""

  chainName: str
  """Network display name, e.g. `BTC`, `Lightning Network`."""
  chainId: str
  """Network identifier used in API calls, e.g. `btc`, `bsc`."""
  withdrawalMinSize: str
  """Minimum withdrawal amount."""
  withdrawMinSize: str
  """Same value as `withdrawalMinSize`; KuCoin's live response includes both spellings, only the first is documented."""
  depositMinSize: str | None
  """Minimum deposit amount, when the network enforces one."""
  withdrawFeeRate: NotRequired[str]
  """Withdrawal fee rate (percentage). Observed absent for at least one currency/chain (HOT/XLM) — not required."""
  withdrawalMinFee: str
  """Minimum withdrawal fee."""
  withdrawMinFee: str
  """Same value as `withdrawalMinFee`; see `withdrawMinSize`."""
  isWithdrawEnabled: bool
  """Whether withdrawal is currently enabled on this network."""
  isDepositEnabled: bool
  """Whether deposit is currently enabled on this network."""
  confirms: int
  """Confirmations required before a deposit is credited."""
  preConfirms: int
  """Confirmations required before a deposit shows as pending."""
  contractAddress: str
  """Token contract address on this network, or empty string for a native asset."""
  withdrawPrecision: int
  """Withdrawal decimal precision."""
  maxWithdraw: str | None
  """Maximum withdrawal amount, when the network enforces one."""
  maxDeposit: str | None
  """Maximum deposit amount, when the network enforces one."""
  needTag: bool
  """Whether a deposit tag/memo is required on this network."""
  addressRegex: str | None
  """Regex a valid deposit address on this network matches, or `null` when deposit is disabled on this network. Undocumented, observed live."""
  memoRegex: str | None
  """Regex a valid deposit tag/memo matches (empty string when `needTag` is false), or `null` when deposit is disabled on this network. Undocumented, observed live."""


class CurrencyDetail(TypedDict):
  """Detail for one currency."""

  currency: str
  """Fixed currency identifier, e.g. `BTC`."""
  name: str
  """Currency name (may be changed by KuCoin)."""
  fullName: str
  """Full currency name, e.g. `Bitcoin`."""
  precision: int
  """Decimal precision."""
  confirms: int | None
  """Confirmations required at the currency level. Observed `null` for every currency — see `notes`; per-chain `confirms` under `chains[]` is what's actually populated."""
  contractAddress: str | None
  """Smart contract address at the currency level. Observed `null` for every currency; per-chain `contractAddress` under `chains[]` is what's actually populated."""
  isMarginEnabled: bool
  """Whether this currency can be margin-traded."""
  isDebitEnabled: bool
  """Whether this currency can be borrowed (debited)."""
  chains: list[CurrencyChain] | None
  """One entry per blockchain network this currency supports, or `null` for a currency with no blockchain (e.g. a fiat currency like `TRY`)."""


_Type = CurrencyDetail
adapter = validator[_Type](_Type)  # type: ignore


class Currency(RpcEndpoint):
  """`Get Currency` — mixed into `Spot`, the product exposing `spot.currency`."""

  async def currency(
    self,
    currency: str,
    *,
    chain: str | None = None,
    validate: bool | None = None,
  ) -> CurrencyDetail:
    """Get detailed information for one currency, including its per-chain deposit/withdrawal parameters and margin/debit trading eligibility.

    Args:
      currency: Currency code, e.g. `BTC`.
      chain: Restrict the response's `chains` to one specific blockchain network.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if chain is not None:
      params['chain'] = chain
    return await self.request(
      'GET',
      f'/api/v3/currencies/{currency}',
      params=params,
      validator=adapter,
      validate=validate,
    )
