from typing_extensions import TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class SettingsEnableTwoFactorStartResponse(TypedDict):
  qrImage: str
  """QR image containing the otpauth URL for Google Authenticator (e.g. data:image/png;base64,iVB...YII=)"""
  secret: str
  """Shared secret key (base-32 encoded)"""
  name: str
  """The name to use with Google Authenticator"""


validate_response = validator(SettingsEnableTwoFactorStartResponse)


class EnableStart(RpcEndpoint):
  async def enable_start(
    self,
    *,
    validate: bool | None = None,
  ) -> SettingsEnableTwoFactorStartResponse:
    """Start the 2FA enablement flow. After calling this endpoint, call `PUT /v1/account/settings/sfa` with a TOTP to finish the process.

    Args:
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/account/POST/v1/account/settings/sfa)
    """
    return await self.authed_request(
      'POST',
      '/v1/account/settings/sfa',
      validator=validate_response,
      validate=validate,
    )
