"""`private/get_user_locks` — `private/get_user_locks`."""

from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class UserLock(TypedDict):
  currency: str
  """Currency this lock status applies to."""
  locked: bool
  """Whether the account is locked in this currency."""
  message: NotRequired[str]
  """Optional information for the user on why the account is locked."""


validate_get_user_locks = validator[list[UserLock]](list[UserLock])


class GetUserLocks(RpcEndpoint):
  """`private/get_user_locks`."""

  async def get_user_locks(self, *, validate: bool | None = None) -> list[UserLock]:
    """Retrieves information about any account locks or restrictions currently active on the authenticated account, per currency. Some locks may prevent trading, withdrawals, or other account operations. Takes no parameters.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-get_user_locks)
    """
    return await self.authed_request(
      'private/get_user_locks', validator=validate_get_user_locks, validate=validate
    )
