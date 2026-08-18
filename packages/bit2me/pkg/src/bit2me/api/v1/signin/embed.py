from typing_extensions import NotRequired, TypedDict
from bit2me.types import TokenResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Session(TypedDict):
  """The embed session opened by this sign-in."""

  id: str
  """Session identifier."""
  expirationTime: int
  """Session expiration time, in Unix epoch milliseconds."""


class SignInEmbedRequest(TypedDict):
  accessToken: str


class SignInEmbedResponse(TypedDict):
  accessToken: TokenResponse
  refreshToken: TokenResponse
  session: NotRequired[Session]


validate_response = validator(SignInEmbedResponse)


class Embed(RpcEndpoint):
  async def embed(
    self,
    sign_in_embed_request: SignInEmbedRequest,
    *,
    validate: bool | None = None,
  ) -> SignInEmbedResponse:
    """Generate access and refresh tokens for the embed session and subsequent API calls.

    Args:
      sign_in_embed_request: Sign-in payload
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/access/POST/v1/signin/embed)
    """
    return await self.request(
      'POST',
      '/v1/signin/embed',
      json=sign_in_embed_request,
      validator=validate_response,
      validate=validate,
    )
