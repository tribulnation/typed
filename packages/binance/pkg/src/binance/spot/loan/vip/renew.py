from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class VipLoanRenewOrder(TypedDict):
  """The renewed VIP loan order."""

  loanAccountId: NotRequired[str]
  """Loan receiving account."""
  loanCoin: NotRequired[str]
  """Borrowed coin."""
  loanAmount: NotRequired[str]
  """Borrowed amount."""
  collateralAccountId: NotRequired[str]
  """Collateral account ID(s), comma-separated."""
  collateralCoin: NotRequired[str]
  """Collateral coin(s), comma-separated."""
  loanTerm: NotRequired[str]
  """New loan term of the renewed order."""


class Renew(RpcEndpoint):
  """Renew an existing VIP loan order for a new term. Available to VIP users only."""

  async def renew(
    self,
    *,
    order_id: int,
    loan_term: int,
    validate: bool | None = None,
  ) -> VipLoanRenewOrder:
    """Renew an existing VIP loan order for a new term. Available to VIP users only.

    Args:
      order_id: Loan order ID to renew.
      loan_term: New loan term in days, e.g. 30 or 60.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-renew)
    """
    params: dict = {
      'orderId': order_id,
      'loanTerm': loan_term,
    }
    _Response = VipLoanRenewOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/loan/vip/renew',
      params=params,
      validator=_validator,
      validate=validate,
    )
