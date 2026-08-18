"""`public/disable_heartbeat` — `public/disable_heartbeat`."""

from typing_extensions import Literal
from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_disable_heartbeat = validator[Literal['ok']](Literal['ok'])  # pyright: ignore[reportArgumentType]  # fmt: skip


class DisableHeartbeat(RpcEndpoint):
  """`public/disable_heartbeat`."""

  async def disable_heartbeat(self, *, validate: bool | None = None) -> Literal['ok']:
    """Stop sending heartbeat messages on this WebSocket connection.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/session-management/public-disable_heartbeat)
    """
    return await self.request(
      'public/disable_heartbeat',
      validator=validate_disable_heartbeat,
      validate=validate,
    )
