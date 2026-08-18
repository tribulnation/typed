from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class VipLoanBorrowInterestRate(TypedDict):
  """Current flexible-rate borrow interest for one loanable coin."""

  asset: NotRequired[str]
  """Loanable coin."""
  flexibleHourlyInterestRate: NotRequired[str]
  """Flexible-rate hourly interest rate, as a decimal string."""
  flexibleDailyInterestRate: NotRequired[str]
  """Flexible-rate daily interest rate, as a decimal string."""
  flexibleYearlyInterestRate: NotRequired[str]
  """Flexible-rate annualized interest rate, as a decimal string."""
  time: NotRequired[str]
  """Millisecond epoch time the rate was computed, as a numeric string."""


class BorrowInterestRate(RpcEndpoint):
  """Get the current VIP loan borrow interest rate for one or more loanable coins."""

  async def borrow_interest_rate(
    self,
    *,
    loan_coin: str,
    validate: bool | None = None,
  ) -> list[VipLoanBorrowInterestRate]:
    """Get the current VIP loan borrow interest rate for one or more loanable coins.

    Args:
      loan_coin: Coins to query, comma-separated. Max 10 assets.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-borrow-interest-rate)
    """
    params: dict = {
      'loanCoin': loan_coin,
    }
    _Response = list[VipLoanBorrowInterestRate]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/loan/vip/request/interestRate',
      params=params,
      validator=_validator,
      validate=validate,
    )
