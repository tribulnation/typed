from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class KycVerificationInitV3request(TypedDict):
  locale: str
  """Locale to render the hosted verification flow in, e.g. `en`."""
  workflowId: NotRequired[Literal[10011]]
  """Workflow id: 10011"""
  successUrl: NotRequired[str]
  """URL the caller is redirected to after a successful verification."""
  errorUrl: NotRequired[str]
  """URL the caller is redirected to when verification fails or is cancelled."""


class KycVerificationInitV3response(TypedDict):
  redirectUrl: NotRequired[str]
  """URL to open in a native browser to complete the hosted KYC verification flow."""
  token: NotRequired[str]
  """Session token identifying this KYC verification attempt."""
  reference: NotRequired[str]
  """Reference identifier correlating this KYC session with Bit2Me's records."""
  provider: NotRequired[Literal['jumio', 'incode']]
  """Third-party identity verification provider handling this KYC session."""


validate_response = validator(KycVerificationInitV3response)


class IdentityVerification(RpcEndpoint):
  async def identity_verification(
    self,
    kyc_verification_init_v3request: KycVerificationInitV3request,
    *,
    validate: bool | None = None,
  ) -> KycVerificationInitV3response:
    """Init KYC verification iframe.
    Open the redirectUrl in a native browser.

    Do NOT open the url in webviews to avoid incompatibilities with screen or camera recording permissions.

    Args:
      kyc_verification_init_v3request: Parameters to start a new hosted KYC verification session.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/kyc/POST/v3/account/verify/identity/init)
    """
    return await self.authed_request(
      'POST',
      '/v3/account/verify/identity/init',
      json=kyc_verification_init_v3request,
      validator=validate_response,
      validate=validate,
    )
