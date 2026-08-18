"""`public/set_heartbeat` — `public/set_heartbeat`."""

from typing_extensions import Literal
from typed_core.validation import validator
from deribit.core import RpcEndpoint

validate_set_heartbeat = validator[Literal['ok']](Literal['ok'])  # pyright: ignore[reportArgumentType]  # fmt: skip


class SetHeartbeat(RpcEndpoint):
  """`public/set_heartbeat`."""

  async def set_heartbeat(
    self,
    *,
    interval: float,
    validate: bool | None = None,
  ) -> Literal['ok']:
    """Signal the WebSocket connection to send and expect heartbeats, used to detect stale connections. Once enabled, the server sends periodic `heartbeat` messages plus intermittent `test_request` challenges; the caller must answer each `test_request` with a `public/test` call or the server closes the connection immediately -- and if Cancel On Disconnect is enabled, any orders opened over that connection are then cancelled.

    Args:
      interval: Heartbeat interval, in seconds. Deribit enforces a minimum of 10 seconds.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/session-management/public-set_heartbeat)
    """
    params: dict = {
      'interval': interval,
    }
    return await self.request(
      'public/set_heartbeat',
      params=params,
      validator=validate_set_heartbeat,
      validate=validate,
    )
