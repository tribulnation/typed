from bit2me.types import BooleanResultResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator

validate_response = validator(BooleanResultResponse)


class Delete(RpcEndpoint):
  async def delete(
    self, *, id: str, validate: bool | None = None
  ) -> BooleanResultResponse:
    """Delete a pocket

    Args:
      id: Id of the pocket to delete.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/wallet/DELETE/v1/wallet/pocket)
    """
    params: dict = {
      'id': id,
    }
    return await self.authed_request(
      'DELETE',
      '/v1/wallet/pocket',
      params=params,
      validator=validate_response,
      validate=validate,
    )
