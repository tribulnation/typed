"""`spot.trading.cancel_all_orders_after` -- private Spot endpoint."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class DeadMansSwitchStatus(TypedDict):
  """Current state of the dead man's switch timer after this call."""

  currentTime: NotRequired[str]
  """RFC3339 timestamp at which the request was received."""
  triggerTime: NotRequired[str]
  """RFC3339 timestamp after which all orders will be cancelled, unless the timer is extended or disabled first. Equal to `currentTime` when the timer was disabled (`timeout: 0`)."""


validate_cancel_all_orders_after = validator(DeadMansSwitchStatus)


class CancelAllOrdersAfter(RpcEndpoint):
  """`spot.trading.cancel_all_orders_after`."""

  async def cancel_all_orders_after(self, timeout: int) -> DeadMansSwitchStatus:
    """A "dead man's switch" that protects against network malfunction, extreme latency, or unexpected matching-engine downtime. Starts a countdown timer (given in seconds) that cancels every one of the client's orders when it expires; each call resets the countdown. Pass a `timeout` of `0` to disable the mechanism. Recommended usage: call every 15-30 seconds with a 60 second timeout, so a brief disconnection doesn't cancel resting orders but a real network breakdown does. Also recommended: disable the timer before scheduled matching-engine maintenance, since a live timer cancels every order when the engine comes back up from any downtime, planned or not.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` or `Orders and trades - Cancel & close orders`

    Args:
      timeout: Duration in seconds to set or extend the timer; must be less than 86400. `0` disables the timer.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/trading/cancel-all-orders-after-x)
    """
    data: dict = {
      'timeout': timeout,
    }

    return await self.authed_request(
      '/0/private/CancelAllOrdersAfter',
      data,
      validator=validate_cancel_all_orders_after,
    )
