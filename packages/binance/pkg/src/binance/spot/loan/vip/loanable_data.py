from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class VipLoanLoanableAsset(TypedDict):
  """One loanable coin's interest rates and borrow limit at a given VIP level."""

  loanCoin: NotRequired[str]
  """Loanable coin."""
  _flexibleDailyInterestRate: NotRequired[str]
  """Flexible-rate daily interest rate, as a decimal string."""
  _flexibleYearlyInterestRate: NotRequired[str]
  """Flexible-rate annualized interest rate, as a decimal string."""
  _30dDailyInterestRate: NotRequired[str]
  """30-day fixed-rate daily interest rate, as a decimal string."""
  _30dYearlyInterestRate: NotRequired[str]
  """30-day fixed-rate annualized interest rate, as a decimal string."""
  _60dDailyInterestRate: NotRequired[str]
  """60-day fixed-rate daily interest rate, as a decimal string."""
  _60dYearlyInterestRate: NotRequired[str]
  """60-day fixed-rate annualized interest rate, as a decimal string."""
  minLimit: NotRequired[str]
  """Minimum borrowable amount, in USD value."""
  maxLimit: NotRequired[str]
  """Maximum borrowable amount, in USD value."""
  vipLevel: NotRequired[int]
  """VIP level this row's rates and limit apply to."""


class VipLoanLoanableAssetDataPage(TypedDict):
  """Loanable asset data. Not observed to accept page parameters despite the `rows`/`total` shape -- see this endpoint's notes."""

  rows: NotRequired[list[VipLoanLoanableAsset]]
  """Matching loanable assets."""
  total: NotRequired[int]
  """Total number of matching loanable assets."""


class LoanableData(RpcEndpoint):
  """Get interest rate and borrow limit of loanable assets, at the caller's VIP level or a specified one. The borrow limit is shown in USD value."""

  async def loanable_data(
    self,
    *,
    loan_coin: str | None = None,
    vip_level: int | None = None,
    validate: bool | None = None,
  ) -> VipLoanLoanableAssetDataPage:
    """Get interest rate and borrow limit of loanable assets, at the caller's VIP level or a specified one. The borrow limit is shown in USD value.

    Args:
      loan_coin: Restrict results to one loanable coin.
      vip_level: VIP level to query interest rates and limits for. Defaults to the caller's own VIP level.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-loanable-assets-data)
    """
    params = {}
    if loan_coin is not None:
      params['loanCoin'] = loan_coin
    if vip_level is not None:
      params['vipLevel'] = vip_level
    _Response = VipLoanLoanableAssetDataPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/loan/vip/loanable/data',
      params=params,
      validator=_validator,
      validate=validate,
    )
