from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class VipLoanRepayResult(TypedDict):
  """The result of a VIP loan repayment."""

  loanCoin: NotRequired[str]
  """Borrowed coin."""
  repayAmount: NotRequired[str]
  """Amount repaid."""
  remainingPrincipal: NotRequired[str]
  """Remaining unpaid principal after this repayment."""
  remainingInterest: NotRequired[str]
  """Remaining unpaid interest after this repayment."""
  collateralCoin: NotRequired[str]
  """Collateral coin(s), comma-separated."""
  currentLTV: NotRequired[str]
  """Current loan-to-value ratio after this repayment, as a decimal string."""
  repayStatus: NotRequired[Literal['Repaid', 'Repaying', 'Failed']]
  """Repayment status."""


class Repay(RpcEndpoint):
  """Repay an existing VIP loan order. Available to VIP users only."""

  async def repay(
    self,
    *,
    order_id: int,
    amount: float,
    validate: bool | None = None,
  ) -> VipLoanRepayResult:
    """Repay an existing VIP loan order. Available to VIP users only.

    Args:
      order_id: Loan order ID to repay.
      amount: Amount to repay.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-repay)
    """
    params: dict = {
      'orderId': order_id,
      'amount': amount,
    }
    _Response = VipLoanRepayResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/loan/vip/repay',
      params=params,
      validator=_validator,
      validate=validate,
    )
