from datetime import datetime
from typing_extensions import NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class LoanOrderResponse(TypedDict):
  orderId: NotRequired[str]
  """Unique identifier of the loan order."""
  createdAt: NotRequired[datetime]
  """When the loan order was created (ISO 8601)."""
  updatedAt: NotRequired[datetime]
  """When the loan order was last updated (ISO 8601)."""
  userId: NotRequired[str]
  """Identifier of the user the loan order belongs to."""
  requestedByUserId: NotRequired[str]
  """Identifier of the user who requested the loan order (may differ from `userId` for subaccounts)."""
  guaranteeCurrency: NotRequired[str]
  """Currency of the collateral used as loan guarantee."""
  guaranteeOriginalAmount: NotRequired[str]
  """Amount of `guaranteeCurrency` originally pledged as collateral."""
  guaranteeAmount: NotRequired[str]
  """Current amount of `guaranteeCurrency` held as collateral."""
  loanCurrency: NotRequired[str]
  """Currency that was borrowed."""
  loanOriginalAmount: NotRequired[str]
  """Amount of `loanCurrency` originally borrowed."""
  loanAmount: NotRequired[str]
  """Current outstanding amount of `loanCurrency`."""
  paybackAmount: NotRequired[str]
  """Amount of `loanCurrency` paid back so far."""
  ltv: NotRequired[str]
  """Current loan-to-value ratio between the loan and the guarantee."""
  apr: NotRequired[str]
  """Annual percentage rate applied to the loan."""
  status: NotRequired[str]
  """Current status of the loan order (e.g. `pending`)."""
  startedAt: NotRequired[datetime]
  """When the loan started (ISO 8601)."""
  finishedAt: NotRequired[datetime]
  """When the loan was fully paid back or closed (ISO 8601)."""
  expiresAt: NotRequired[datetime]
  """When the loan order expires (ISO 8601)."""
  paybackPrincipalAmount: NotRequired[str]
  """Portion of `paybackAmount` applied to the loan principal."""
  paybackInterestAmount: NotRequired[str]
  """Portion of `paybackAmount` applied to accrued interest."""
  interestAmount: NotRequired[str]
  """Total interest accrued on the loan so far."""
  loanAmountConverted: NotRequired[str]
  """`loanAmount` converted to the user's fiat currency."""
  paybackAmountConverted: NotRequired[str]
  """`paybackAmount` converted to the user's fiat currency."""
  guaranteeAmountConverted: NotRequired[str]
  """`guaranteeAmount` converted to the user's fiat currency."""
  remainingAmount: NotRequired[str]
  """Remaining amount of `loanCurrency` still owed."""
  remainingAmountConverted: NotRequired[str]
  """`remainingAmount` converted to the user's fiat currency."""
  remainingPrincipalAmount: NotRequired[str]
  """Remaining principal still owed."""
  remainingInterestAmount: NotRequired[str]
  """Remaining accrued interest still owed."""
  liquidationPriceReference: NotRequired[str]
  """Reference price of the guarantee currency at which the loan would be liquidated."""
  discount: NotRequired[str]
  """Discount applied to the loan."""
  isUserApprovalRequired: NotRequired[bool]
  """Whether the user still needs to approve this loan order."""


validate_response = validator(LoanOrderResponse)


class Get(RpcEndpoint):
  async def get(
    self, order_id: str, *, validate: bool | None = None
  ) -> LoanOrderResponse:
    """Get a user loan order

    Args:
      order_id: Identifier of the loan order to fetch.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/loan/GET/v1/loan/orders/{orderId})
    """
    return await self.authed_request(
      'GET',
      f'/v1/loan/orders/{order_id}',
      validator=validate_response,
      validate=validate,
    )
