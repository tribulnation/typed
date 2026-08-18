from typing_extensions import TypedDict
from bit2me.types import LoanAction
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class PaybackGuaranteeRequest(TypedDict):
  paybackAmount: str
  """Amount of the loan order's loan currency to pay back."""


validate_response = validator(LoanAction)


class Payback(RpcEndpoint):
  async def payback(
    self,
    order_id: str,
    payback_guarantee_request: PaybackGuaranteeRequest,
    *,
    validate: bool | None = None,
  ) -> LoanAction:
    """Process a payment to refund a specified amount of an loan. This action will complete the loan if the outstanding amount is fully paid.

    Args:
      order_id: Identifier of the loan order to pay back.
      payback_guarantee_request: Amount to pay back on the loan order.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/loan/POST/v1/loan/orders/{orderId}/payback)
    """
    return await self.authed_request(
      'POST',
      f'/v1/loan/orders/{order_id}/payback',
      json=payback_guarantee_request,
      validator=validate_response,
      validate=validate,
    )
