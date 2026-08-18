from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProBankruptcyLoanAmount(TypedDict):
  """Bankruptcy loan amount."""

  asset: NotRequired[str]
  """Asset name."""
  amount: NotRequired[str]
  """Portfolio margin bankruptcy loan amount, in BUSD."""


class BankruptcyLoanAmount(RpcEndpoint):
  """Query Portfolio Margin Pro Bankruptcy Loan Amount"""

  async def bankruptcy_loan_amount(
    self,
    *,
    validate: bool | None = None,
  ) -> PmProBankruptcyLoanAmount:
    """Query Portfolio Margin Pro Bankruptcy Loan Amount.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#query-portfolio-margin-pro-bankruptcy-loan-amount)
    """
    _Response = PmProBankruptcyLoanAmount
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/portfolio/pmLoan', validator=_validator, validate=validate
    )
