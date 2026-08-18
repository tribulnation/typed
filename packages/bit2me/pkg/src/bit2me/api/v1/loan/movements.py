from datetime import datetime
from typing_extensions import NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class FeeAmountLiquidated(TypedDict):
  """Fee amount liquidated as part of this movement."""

  value: NotRequired[str]
  """Amount value."""
  currency: NotRequired[str]
  """Currency of `value`."""
  converted: NotRequired[str]
  """`value` converted to `convertedCurrency`."""
  convertedCurrency: NotRequired[str]
  """Currency `value` is converted to."""


class GuaranteeAmount(TypedDict):
  """Guarantee amount involved in the movement."""

  value: NotRequired[str]
  """Amount value."""
  currency: NotRequired[str]
  """Currency of `value`."""
  converted: NotRequired[str]
  """`value` converted to `convertedCurrency`."""
  convertedCurrency: NotRequired[str]
  """Currency `value` is converted to."""


class GuaranteeAmountLiquidated(TypedDict):
  """Guarantee amount liquidated as part of this movement."""

  value: NotRequired[str]
  """Amount value."""
  currency: NotRequired[str]
  """Currency of `value`."""
  converted: NotRequired[str]
  """`value` converted to `convertedCurrency`."""
  convertedCurrency: NotRequired[str]
  """Currency `value` is converted to."""


class LoanAmount(TypedDict):
  """Loan amount involved in the movement."""

  value: NotRequired[str]
  """Amount value."""
  currency: NotRequired[str]
  """Currency of `value`."""
  converted: NotRequired[str]
  """`value` converted to `convertedCurrency`."""
  convertedCurrency: NotRequired[str]
  """Currency `value` is converted to."""


class PaybackAmount(TypedDict):
  """Payback amount involved in the movement."""

  value: NotRequired[str]
  """Amount value."""
  currency: NotRequired[str]
  """Currency of `value`."""
  converted: NotRequired[str]
  """`value` converted to `convertedCurrency`."""
  convertedCurrency: NotRequired[str]
  """Currency `value` is converted to."""


class LoanMovementPayload(TypedDict):
  """Movement-specific details."""

  ltv: NotRequired[str]
  """Loan-to-value ratio at the time of the movement."""
  previousLtv: NotRequired[str]
  """Loan-to-value ratio before the movement."""
  liquidationLtv: NotRequired[str]
  """Loan-to-value ratio at which the loan would be liquidated."""
  guaranteeAmount: NotRequired[GuaranteeAmount]
  isCompleted: NotRequired[bool]
  """Whether the movement has completed."""
  loanAmount: NotRequired[LoanAmount]
  paybackAmount: NotRequired[PaybackAmount]
  guaranteeAmountLiquidated: NotRequired[GuaranteeAmountLiquidated]
  feeAmountLiquidated: NotRequired[FeeAmountLiquidated]
  isPromotional: NotRequired[bool]
  """Whether the movement is part of a promotional loan."""


class LoanMovement(TypedDict):
  movementId: NotRequired[str]
  """Unique identifier of the movement."""
  orderId: NotRequired[str]
  """Identifier of the loan order this movement belongs to."""
  userId: NotRequired[str]
  """Identifier of the user the movement belongs to."""
  type: NotRequired[str]
  """Kind of loan movement (e.g. `request`)."""
  createdAt: NotRequired[datetime]
  """When the movement was created (ISO 8601)."""
  updatedAt: NotRequired[datetime]
  """When the movement was last updated (ISO 8601)."""
  payload: NotRequired[LoanMovementPayload]


class ListLoanMovementsResponse(TypedDict):
  total: NotRequired[int]
  """Total number of loan movements matching the query."""
  data: NotRequired[list[LoanMovement]]
  """Page of loan movements."""


validate_response = validator(ListLoanMovementsResponse)


class Movements(RpcEndpoint):
  async def __call__(
    self,
    *,
    order_id: str | None = None,
    limit: float | None = None,
    offset: float | None = None,
    validate: bool | None = None,
  ) -> ListLoanMovementsResponse:
    """Get loan user movements

    Args:
      order_id: Restrict movements to a single loan order.
      limit: The maximum number of rows to fetch
      offset: The number of rows to skip, for pagination.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/loan/GET/v1/loan/movements)
    """
    params = {}
    if order_id is not None:
      params['orderId'] = order_id
    if limit is not None:
      params['limit'] = limit
    if offset is not None:
      params['offset'] = offset
    return await self.authed_request(
      'GET',
      '/v1/loan/movements',
      params=params,
      validator=validate_response,
      validate=validate,
    )
