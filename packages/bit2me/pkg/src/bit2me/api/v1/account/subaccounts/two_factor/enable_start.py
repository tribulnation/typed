from typing_extensions import TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class InitSubaccountTwoFactorRequest(TypedDict):
  subaccountUserId: str


class InitSubaccountTwoFactorResponse(TypedDict):
  secret: str
  """TOTP secret for the subaccount to register in a Google Authenticator-compatible app to finish enabling 2FA."""


validate_response = validator(InitSubaccountTwoFactorResponse)


class EnableStart(RpcEndpoint):
  async def enable_start(
    self,
    init_subaccount_two_factor_request: InitSubaccountTwoFactorRequest,
    *,
    validate: bool | None = None,
  ) -> InitSubaccountTwoFactorResponse:
    """Start the Google Authenticator 2FA enablement flow for a subaccount.

    Args:
      init_subaccount_two_factor_request: The details to init subaccount 2fa process
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/POST/v1/account/subaccount/sfa)
    """
    return await self.authed_request(
      'POST',
      '/v1/account/subaccount/sfa',
      json=init_subaccount_two_factor_request,
      validator=validate_response,
      validate=validate,
    )
