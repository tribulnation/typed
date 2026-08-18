"""`GET /api/v1/account-overview-all` — account.sub_account.list_futures_balance."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesSubAccountBalance(TypedDict):
  accountName: str
  """Account name; the master account itself reports as `main`."""
  accountEquity: float
  """Account equity."""
  unrealisedPNL: float
  """Unrealized profit/loss."""
  marginBalance: float
  """Margin balance."""
  positionMargin: float
  """Margin held by open positions."""
  orderMargin: float
  """Margin held by open orders."""
  frozenFunds: float
  """Funds frozen for withdrawal/out-transfer."""
  availableBalance: float
  """Available balance."""
  availableMargin: float
  """Available margin. Not documented by KuCoin's docs-portal/SDK spec; observed on the live response and added here."""
  currency: str
  """Currency this entry is denominated in."""


class FuturesSubAccountOverviewSummary(TypedDict):
  """Totals across the master account and every sub-account."""

  accountEquityTotal: float
  """Total account equity."""
  unrealisedPNLTotal: float
  """Total unrealized profit/loss."""
  marginBalanceTotal: float
  """Total margin balance."""
  positionMarginTotal: float
  """Total margin held by open positions."""
  orderMarginTotal: float
  """Total margin held by open orders."""
  frozenFundsTotal: float
  """Total funds frozen for withdrawal/out-transfer."""
  availableBalanceTotal: float
  """Total available balance."""
  availableMarginTotal: float
  """Total available margin. Not documented by KuCoin's docs-portal/SDK spec; observed on the live response and added here."""
  currency: str
  """Currency the totals are denominated in."""


class FuturesSubAccountOverview(TypedDict):
  summary: FuturesSubAccountOverviewSummary
  accounts: list[FuturesSubAccountBalance]
  """One entry per account -- the master account (`accountName: "main"`) plus every sub-account."""


_Type = FuturesSubAccountOverview
adapter = validator[_Type](_Type)  # type: ignore


class ListFuturesBalance(RpcEndpoint):
  """`account.sub_account.list_futures_balance` — mixed into `SubAccount`, the product exposing `account.sub_account.list_futures_balance`."""

  async def list_futures_balance(
    self,
    *,
    currency: str | None = None,
    validate: bool | None = None,
  ) -> FuturesSubAccountOverview:
    """Get a Futures account overview covering the master account and every one of its sub-accounts, aggregated into one summary plus a per-account breakdown.

    Args:
      currency: Currency to report balances in.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    return await self.authed_request(
      'GET',
      '/api/v1/account-overview-all',
      params=params,
      validator=adapter,
      validate=validate,
    )
