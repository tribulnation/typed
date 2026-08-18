from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FlexibleLoanBorrowOrder(TypedDict):
  """The submitted flexible rate crypto loan borrow order."""

  loanCoin: NotRequired[str]
  """Borrowed coin."""
  loanAmount: NotRequired[str]
  """Borrowed amount."""
  collateralCoin: NotRequired[str]
  """Collateral coin."""
  collateralAmount: NotRequired[str]
  """Pledged collateral amount."""
  status: NotRequired[str]
  """Borrow result."""


class Borrow(RpcEndpoint):
  """Borrow a flexible rate crypto loan against collateral. Available for both master and sub-accounts."""

  async def borrow(
    self,
    *,
    loan_coin: str,
    collateral_coin: str,
    loan_amount: float | None = None,
    collateral_amount: float | None = None,
    validate: bool | None = None,
  ) -> FlexibleLoanBorrowOrder:
    """Borrow a flexible rate crypto loan against collateral. Available for both master and sub-accounts.

    Args:
      loan_coin: Coin to borrow.
      collateral_coin: Collateral coin.
      loan_amount: Amount to borrow. Mandatory when `collateralAmount` is empty; the two are mutually exclusive ways of sizing the loan.
      collateral_amount: Amount of collateral to pledge. Mandatory when `loanAmount` is empty; the two are mutually exclusive ways of sizing the loan.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-crypto-loan/api/rest-api/flexible-rate#flexible-loan-borrow)
    """
    params: dict = {
      'loanCoin': loan_coin,
      'collateralCoin': collateral_coin,
    }
    if loan_amount is not None:
      params['loanAmount'] = loan_amount
    if collateral_amount is not None:
      params['collateralAmount'] = collateral_amount
    _Response = FlexibleLoanBorrowOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v2/loan/flexible/borrow',
      params=params,
      validator=_validator,
      validate=validate,
    )
