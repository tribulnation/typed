from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FlexibleLoanRepayment(TypedDict):
  """The result of repaying a flexible rate crypto loan."""

  loanCoin: NotRequired[str]
  """Loan coin."""
  collateralCoin: NotRequired[str]
  """Collateral coin."""
  remainingDebt: NotRequired[str]
  """Remaining debt after this repayment."""
  remainingCollateral: NotRequired[str]
  """Remaining collateral after this repayment."""
  fullRepayment: NotRequired[bool]
  """Echo of the requested `fullRepayment`."""
  currentLTV: NotRequired[str]
  """LTV after this repayment."""
  repayStatus: NotRequired[Literal['REPAID', 'REPAYING', 'FAILED']]
  """Repayment result."""


class Repay(RpcEndpoint):
  """Repay a flexible rate crypto loan, in loan asset or collateral, fully or partially."""

  async def repay(
    self,
    *,
    loan_coin: str,
    collateral_coin: str,
    repay_amount: float,
    collateral_return: bool | None = None,
    full_repayment: bool | None = None,
    repayment_type: Literal[1, 2] | None = None,
    validate: bool | None = None,
  ) -> FlexibleLoanRepayment:
    """Repay a flexible rate crypto loan, in loan asset or collateral, fully or partially.

    Args:
      loan_coin: Loan coin.
      collateral_coin: Collateral coin.
      repay_amount: Amount to repay. Mandatory even when `fullRepayment` is `false`.
      collateral_return: `true` returns extra collateral to the spot account after repayment; `false` keeps extra collateral in the order and lowers LTV.
      full_repayment: `true` for full repayment; `false` for partial repayment based on `repayAmount`.
      repayment_type: Asset used to repay: `1` repays with the loan asset, `2` repays with collateral.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-crypto-loan/api/rest-api/flexible-rate#flexible-loan-repay)
    """
    params: dict = {
      'loanCoin': loan_coin,
      'collateralCoin': collateral_coin,
      'repayAmount': repay_amount,
    }
    if collateral_return is not None:
      params['collateralReturn'] = collateral_return
    if full_repayment is not None:
      params['fullRepayment'] = full_repayment
    if repayment_type is not None:
      params['repaymentType'] = repayment_type
    _Response = FlexibleLoanRepayment
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v2/loan/flexible/repay',
      params=params,
      validator=_validator,
      validate=validate,
    )
