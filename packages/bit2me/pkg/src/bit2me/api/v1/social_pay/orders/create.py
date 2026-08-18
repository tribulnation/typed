from typing_extensions import NotRequired, TypedDict
from bit2me.types import PayOrderData, PayOrderType, Phone
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class SocialPayOrderRequest(TypedDict):
  pocketId: str
  type: PayOrderType
  email: NotRequired[str]
  phone: NotRequired[Phone]
  alias: NotRequired[str]
  amount: str
  currency: str
  """Valid currency symbol"""
  note: NotRequired[str]


validate_response = validator(PayOrderData)


class Create(RpcEndpoint):
  async def create(
    self,
    social_pay_order_request: SocialPayOrderRequest,
    *,
    validate: bool | None = None,
  ) -> PayOrderData:
    """Creates a new payment order

    Args:
      social_pay_order_request: The social-pay order to create: recipient (by pocket, email, phone or alias), amount and currency.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/transfers/POST/v1/social-pay/order)
    """
    return await self.authed_request(
      'POST',
      '/v1/social-pay/order',
      json=social_pay_order_request,
      validator=validate_response,
      validate=validate,
    )
