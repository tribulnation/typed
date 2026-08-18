"""`spot.market_data.system_status` -- public Spot market data."""

from datetime import datetime
from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class SystemStatus(TypedDict):
  """The exchange's current operational status."""

  status: NotRequired[Literal['online', 'maintenance', 'cancel_only', 'post_only']]
  """Current system status: `online` (operating normally, all order types accepted), `maintenance` (offline, no new orders or cancellations), `cancel_only` (resting orders can be cancelled but none submitted, no trades occur), or `post_only` (only post-only limit orders accepted, existing orders may still be cancelled, no trades occur)."""
  timestamp: NotRequired[datetime]
  """Current timestamp (RFC3339)."""


validate_system_status = validator(SystemStatus)


class SystemStatusEndpoint(RpcEndpoint):
  """`spot.market_data.system_status`."""

  async def system_status(self) -> SystemStatus:
    """Get the current system status or trading mode.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/market-data/get-system-status)
    """
    return await self.request(
      '/0/public/SystemStatus', validator=validate_system_status
    )
