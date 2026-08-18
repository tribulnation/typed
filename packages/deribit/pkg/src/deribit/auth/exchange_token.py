"""`public/exchange_token` — `public/exchange_token`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class ExchangeTokenResult(TypedDict):
  """Result of a successful public/exchange_token call."""

  access_token: str
  """Access token scoped to the new subject id."""
  token_type: Literal['bearer']
  """Authorization type; always `bearer`."""
  expires_in: int
  """Token lifetime, in seconds."""
  refresh_token: str
  """Refresh token for the new subject id's session."""
  scope: str
  """Access scope actually granted to the new token."""
  sid: NotRequired[str]
  """Session id."""


validate_exchange_token = validator[ExchangeTokenResult](ExchangeTokenResult)


class ExchangeToken(RpcEndpoint):
  """`public/exchange_token`."""

  async def exchange_token(
    self,
    *,
    refresh_token: str,
    subject_id: int,
    scope: str | None = None,
    validate: bool | None = None,
  ) -> ExchangeTokenResult:
    """Generate a token for a new subject id, to switch between subaccounts without a full re-authentication.

    Args:
      refresh_token: Refresh token from an earlier public/auth (or exchange_token/fork_token) call.
      subject_id: The subaccount id to act as. Must differ from the caller's current subject id.
      scope: Optional scope override for the new session; cannot exceed the caller's own permissions. Supports `session` scope for direct session creation during token exchange.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/authentication/public-exchange_token)
    """
    params: dict = {
      'refresh_token': refresh_token,
      'subject_id': subject_id,
    }
    if scope is not None:
      params['scope'] = scope
    return await self.request(
      'public/exchange_token',
      params=params,
      validator=validate_exchange_token,
      validate=validate,
    )
