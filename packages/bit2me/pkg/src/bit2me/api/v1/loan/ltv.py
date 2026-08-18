from typing_extensions import NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class LoanLtvResponse(TypedDict):
  guaranteeCurrency: NotRequired[str]
  """Currency of the collateral used as loan guarantee."""
  guaranteeAmount: NotRequired[str]
  """Amount of `guaranteeCurrency`, as provided or as calculated from `loanAmount`."""
  guaranteeAmountConverted: NotRequired[str]
  """`guaranteeAmount` converted to `userCurrency`."""
  loanCurrency: NotRequired[str]
  """Currency to borrow."""
  loanAmount: NotRequired[str]
  """Amount of `loanCurrency`, as provided or as calculated from `guaranteeAmount`."""
  loanAmountConverted: NotRequired[str]
  """`loanAmount` converted to `userCurrency`."""
  apr: NotRequired[str]
  """Annual percentage rate that would apply to the loan."""
  ltv: NotRequired[str]
  """Resulting loan-to-value ratio between the loan and the guarantee."""
  userCurrency: NotRequired[str]
  """Fiat currency the guarantee and loan amounts are converted to for display."""


validate_response = validator(LoanLtvResponse)


class Ltv(RpcEndpoint):
  async def __call__(
    self,
    *,
    guarantee_currency: str,
    guarantee_amount: str | None = None,
    loan_currency: str,
    loan_amount: str | None = None,
    user_currency: str,
    validate: bool | None = None,
  ) -> LoanLtvResponse:
    """Get the calculated LTV (Loan To Value). You should provide one of (and only) loanAmount or guaranteeAmount

    Args:
      guarantee_currency: Currency of the collateral used as loan guarantee.
      guarantee_amount: Amount of `guaranteeCurrency` to use as collateral. Provide this or `loanAmount`, not both.
      loan_currency: Currency to borrow.
      loan_amount: Amount of `loanCurrency` to borrow. Provide this or `guaranteeAmount`, not both.
      user_currency: Fiat currency the guarantee and loan amounts are converted to for display.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/loan/GET/v1/loan/ltv)
    """
    params: dict = {
      'guaranteeCurrency': guarantee_currency,
      'loanCurrency': loan_currency,
      'userCurrency': user_currency,
    }
    if guarantee_amount is not None:
      params['guaranteeAmount'] = guarantee_amount
    if loan_amount is not None:
      params['loanAmount'] = loan_amount
    return await self.authed_request(
      'GET',
      '/v1/loan/ltv',
      params=params,
      validator=validate_response,
      validate=validate,
    )
