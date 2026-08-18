from typing_extensions import NotRequired, TypedDict
from bit2me.types import BooleanResultResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class SettingsEnableTwoFactorEndRequest(TypedDict):
  totp: str
  sessionId: NotRequired[str]
  alwaysRequired: NotRequired[bool]


validate_response = validator(BooleanResultResponse)


class EnableFinish(RpcEndpoint):
  async def enable_finish(
    self,
    settings_enable_two_factor_end_request: SettingsEnableTwoFactorEndRequest,
    *,
    validate: bool | None = None,
  ) -> BooleanResultResponse:
    """Finish the 2FA enablement flow by confirming that the client and server TOTP values match.

    Args:
      settings_enable_two_factor_end_request: The details to end the process
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/PUT/v1/account/settings/sfa)
    """
    return await self.authed_request(
      'put',
      '/v1/account/settings/sfa',
      json=settings_enable_two_factor_end_request,
      validator=validate_response,
      validate=validate,
    )
