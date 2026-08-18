from bit2me.types import PayOrderData
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator

ListResponse = list[PayOrderData]

validate_response = validator(ListResponse)


class List(RpcEndpoint):
  async def list(self, *, validate: bool | None = None) -> ListResponse:
    """Get all pending pay order of a user

    Args:
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/transfers/GET/v1/social-pay/order)
    """
    return await self.authed_request(
      'GET',
      '/v1/social-pay/order',
      validator=validate_response,
      validate=validate,
    )
