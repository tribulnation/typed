from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class SignInTwoFactorV3response(TypedDict):
  sfaType: Literal['gauth', 'email', 'sms', 'call', 'whatsapp']
  """Second-factor verification method currently active for the account, and the one this call initializes."""
  retryIntervalSeconds: NotRequired[float]
  """Seconds to wait before a new verification code can be requested, when `sfaType` sends one (e.g. `sms`, `call`, `whatsapp`, `email`)."""


validate_response = validator(SignInTwoFactorV3response)


class TwoFactor(RpcEndpoint):
  async def two_factor(
    self, *, validate: bool | None = None
  ) -> SignInTwoFactorV3response:
    """Get the active user verification method and initialize the verification process.

    Args:
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/access/GET/v3/signin/sfa)
    """
    return await self.authed_request(
      'GET',
      '/v3/signin/sfa',
      validator=validate_response,
      validate=validate,
    )
