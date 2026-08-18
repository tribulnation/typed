from typing_extensions import TypedDict
from bit2me.types import Phone
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class CreateSubaccountResponse(TypedDict):
  userId: str
  """Unique identifier of the newly created subaccount."""


class CreateSubaccountRequest(TypedDict):
  email: str
  name: str
  surname: str
  phone: Phone


validate_response = validator(CreateSubaccountResponse)


class Create(RpcEndpoint):
  async def __call__(
    self,
    create_subaccount_request: CreateSubaccountRequest,
    *,
    validate: bool | None = None,
  ) -> CreateSubaccountResponse:
    """Create a subaccount.

    Args:
      create_subaccount_request: The details to create the subaccount
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/POST/v1/account/subaccount)
    """
    return await self.authed_request(
      'POST',
      '/v1/account/subaccount',
      json=create_subaccount_request,
      validator=validate_response,
      validate=validate,
    )
