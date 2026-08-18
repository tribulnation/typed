from typing_extensions import TypedDict
from bit2me.types import BooleanResultResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class EndSubaccountTwoFactorRequest(TypedDict):
  subaccountUserId: str
  totp: str


validate_response = validator(BooleanResultResponse)


class EnableFinish(RpcEndpoint):
  async def enable_finish(
    self,
    end_subaccount_two_factor_request: EndSubaccountTwoFactorRequest,
    *,
    validate: bool | None = None,
  ) -> BooleanResultResponse:
    """Finish the Google Authenticator 2FA enablement flow for a subaccount.

    Args:
      end_subaccount_two_factor_request: The details to end subaccount 2fa process
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/PUT/v1/account/subaccount/sfa)
    """
    return await self.authed_request(
      'put',
      '/v1/account/subaccount/sfa',
      json=end_subaccount_two_factor_request,
      validator=validate_response,
      validate=validate,
    )
