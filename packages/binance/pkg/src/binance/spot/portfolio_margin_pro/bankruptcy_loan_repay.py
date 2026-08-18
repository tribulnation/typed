from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProBankruptcyLoanRepay(TypedDict):
  """Bankruptcy loan repay result."""

  tranId: NotRequired[int]
  """Transaction ID."""


class BankruptcyLoanRepay(RpcEndpoint):
  """Portfolio Margin Pro Bankruptcy Loan Repay"""

  async def bankruptcy_loan_repay(
    self,
    *,
    from_: Literal['SPOT', 'MARGIN'] | None = None,
    validate: bool | None = None,
  ) -> PmProBankruptcyLoanRepay:
    """Repay Portfolio Margin Pro Bankruptcy Loan.

    Args:
      from_: Source account to repay from.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#portfolio-margin-pro-bankruptcy-loan-repay)
    """
    params = {}
    if from_ is not None:
      params['from'] = from_
    _Response = PmProBankruptcyLoanRepay
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/portfolio/repay',
      params=params,
      validator=_validator,
      validate=validate,
    )
