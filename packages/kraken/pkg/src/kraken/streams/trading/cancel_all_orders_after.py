"""`streams.trading.cancel_all_orders_after` -- WebSocket trading method."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.ws_rpc import WsRpcEndpoint


class CancelAllOrdersAfterResult(TypedDict):
  """Result of a successful `cancel_all_orders_after` call."""

  currentTime: NotRequired[str]
  """RFC3339 engine time at which the request was received."""
  triggerTime: NotRequired[str]
  """RFC3339 time after which all orders will be cancelled, unless the timer is extended or disabled first."""


validate_cancel_all_orders_after = validator(CancelAllOrdersAfterResult)


class CancelAllOrdersAfter(WsRpcEndpoint):
  """`streams.trading.cancel_all_orders_after`."""

  async def cancel_all_orders_after(self, timeout: int) -> CancelAllOrdersAfterResult:
    """\"Dead Man's Switch": protects against network malfunction, extreme latency, or unexpected matching-engine downtime by starting a countdown timer in the trading engine that cancels all account orders on expiry. The client must keep sending requests to push back the trigger time, or send `timeout: 0` to disable the mechanism. Once the timer expires, all orders are cancelled and the feature stays disabled until the next request. Recommended use: a call every 15-30 seconds with `timeout: 60`. It is also recommended to disable the timer ahead of scheduled trading-engine maintenance, since a still-armed timer cancels all orders when the engine returns from downtime.

    Args:
      timeout: Duration in seconds to set/extend the timer; should be less than 86400 seconds. A timeout of `0` disables the mechanism.

    References:
      - [Official docs](https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/cancel_after)
    """
    params: dict = {
      'timeout': timeout,
    }

    return await self.request(
      'cancel_all_orders_after', params, validator=validate_cancel_all_orders_after
    )
