"""`private/unsubscribe_all` — `private/unsubscribe_all`."""

from typing_extensions import Literal
from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_authed_unsubscribe_all = validator[Literal['ok']](Literal['ok'])  # pyright: ignore[reportArgumentType]  # fmt: skip


class AuthedUnsubscribeAll(RpcEndpoint):
  """`private/unsubscribe_all`."""

  async def authed_unsubscribe_all(
    self, *, validate: bool | None = None
  ) -> Literal['ok']:
    """Unsubscribe from all the channels subscribed so far on this connection. This method takes no parameters.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/subscription-management/private-unsubscribe_all)
    """
    return await self.authed_request(
      'private/unsubscribe_all',
      validator=validate_authed_unsubscribe_all,
      validate=validate,
    )
