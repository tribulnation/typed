from typing_extensions import NotRequired, TypedDict
from bit2me.types import TokenResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class SignInApiKeyRequest(TypedDict):
  userId: NotRequired[str]
  """Identifier of the user to sign in as. Omit to sign in as the API key's own owner."""


class SignInApiKeyResponse(TypedDict):
  accessToken: TokenResponse


validate_response = validator(SignInApiKeyResponse)


class ApiKey(RpcEndpoint):
  async def api_key(
    self,
    sign_in_api_key_request: SignInApiKeyRequest,
    *,
    validate: bool | None = None,
  ) -> SignInApiKeyResponse:
    """Authorize a user with an API key.

    Args:
      sign_in_api_key_request: Sign-in payload
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/access/POST/v1/signin/apikey)
    """
    return await self.authed_request(
      'POST',
      '/v1/signin/apikey',
      json=sign_in_api_key_request,
      validator=validate_response,
      validate=validate,
    )
