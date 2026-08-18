from bit2me.types import OrderResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator

validate_response = validator(OrderResponse)


class Get(RpcEndpoint):
  async def get(self, id: str, *, validate: bool | None = None) -> OrderResponse:
    """Get order details by order identifier.

    Args:
      id: Identifier of the order to retrieve.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/trading/GET/v1/trading/order/{id})
    """
    return await self.authed_request(
      'GET',
      f'/v1/trading/order/{id}',
      validator=validate_response,
      validate=validate,
    )
