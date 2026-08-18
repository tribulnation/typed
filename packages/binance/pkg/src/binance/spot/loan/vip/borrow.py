from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class VipLoanBorrowOrder(TypedDict):
  """The submitted VIP loan borrow order."""

  loanAccountId: NotRequired[str]
  """Loan receiving account."""
  requestId: NotRequired[str]
  """Borrow request ID."""
  loanCoin: NotRequired[str]
  """Borrowed coin."""
  isFlexibleRate: NotRequired[str]
  """Echo of the requested rate mode (`TRUE` for flexible, `FALSE` for fixed)."""
  loanAmount: NotRequired[str]
  """Borrowed amount."""
  collateralAccountId: NotRequired[str]
  """Echo of the requested collateral account ID(s), comma-separated."""
  collateralCoin: NotRequired[str]
  """Echo of the requested collateral coin(s), comma-separated."""
  loanTerm: NotRequired[str]
  """Loan term of the resulting order."""


class Borrow(RpcEndpoint):
  """Submit a VIP loan borrow request. Available to VIP users only."""

  async def borrow(
    self,
    *,
    loan_account_id: int,
    loan_coin: str,
    loan_amount: float,
    collateral_account_id: str,
    collateral_coin: str,
    is_flexible_rate: bool,
    loan_term: int | None = None,
    validate: bool | None = None,
  ) -> VipLoanBorrowOrder:
    """Submit a VIP loan borrow request. Available to VIP users only.

    Args:
      loan_account_id: Loan receiving account ID. Must be under the same master account as `collateralAccountId`; only master account applications are supported.
      loan_coin: Coin to borrow.
      loan_amount: Amount to borrow.
      collateral_account_id: Collateral account ID(s) securing the loan, comma-separated for multiple.
      collateral_coin: Collateral coin(s) securing the loan, comma-separated for multiple.
      is_flexible_rate: `true` for a flexible rate loan, `false` for a fixed rate loan.
      loan_term: Loan term in days, e.g. 30 or 60. Mandatory when `isFlexibleRate` is `false`; optional for a flexible rate loan.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-borrow)
    """
    params: dict = {
      'loanAccountId': loan_account_id,
      'loanCoin': loan_coin,
      'loanAmount': loan_amount,
      'collateralAccountId': collateral_account_id,
      'collateralCoin': collateral_coin,
      'isFlexibleRate': is_flexible_rate,
    }
    if loan_term is not None:
      params['loanTerm'] = loan_term
    _Response = VipLoanBorrowOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/loan/vip/borrow',
      params=params,
      validator=_validator,
      validate=validate,
    )
