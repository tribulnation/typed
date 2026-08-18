"""`public/fork_token` — `public/fork_token`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class ForkTokenResult(TypedDict):
  """Result of a successful public/fork_token call."""

  access_token: str
  """Access token for the new forked session."""
  token_type: Literal['bearer']
  """Authorization type; always `bearer`."""
  expires_in: int
  """Token lifetime, in seconds."""
  refresh_token: str
  """Refresh token for the new forked session."""
  scope: str
  """Access scope of the new session, e.g. `session:<session_name> ...`."""
  sid: NotRequired[str]
  """Session id."""


validate_fork_token = validator[ForkTokenResult](ForkTokenResult)


class ForkToken(RpcEndpoint):
  """`public/fork_token`."""

  async def fork_token(
    self,
    *,
    refresh_token: str,
    session_name: str,
    validate: bool | None = None,
  ) -> ForkTokenResult:
    """Generate a token for a new named session, cloned from a session-scoped token.

    Args:
      refresh_token: Refresh token from an earlier public/auth call, scoped session:name.
      session_name: Name of the new session to create.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/authentication/public-fork_token)
    """
    params: dict = {
      'refresh_token': refresh_token,
      'session_name': session_name,
    }
    return await self.request(
      'public/fork_token',
      params=params,
      validator=validate_fork_token,
      validate=validate,
    )
