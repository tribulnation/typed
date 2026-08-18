from typing_extensions import NotRequired, TypedDict
from bit2me.types import BooleanResultResponse, PocketColor
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class UpdateWalletPocketRequest(TypedDict):
  id: str
  name: NotRequired[str]
  color: NotRequired[PocketColor]


validate_response = validator(BooleanResultResponse)


class Update(RpcEndpoint):
  async def update(
    self,
    update_wallet_pocket_request: UpdateWalletPocketRequest,
    *,
    validate: bool | None = None,
  ) -> BooleanResultResponse:
    """Update pocket data

    Args:
      update_wallet_pocket_request: Id of the pocket to update, and the fields to change.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/wallet/PUT/v1/wallet/pocket)
    """
    return await self.authed_request(
      'put',
      '/v1/wallet/pocket',
      json=update_wallet_pocket_request,
      validator=validate_response,
      validate=validate,
    )
