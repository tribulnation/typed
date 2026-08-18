"""`streams.trading.cancel_all` -- WebSocket trading method."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.ws_rpc import WsRpcEndpoint


class CancelAllResult(TypedDict):
  """Result of a successful `cancel_all` call."""

  count: NotRequired[int]
  """Number of orders cancelled."""
  warnings: NotRequired[list[str]]
  """Non-fatal warnings about the cancellation, if any."""


validate_cancel_all = validator(CancelAllResult)


class CancelAll(WsRpcEndpoint):
  """`streams.trading.cancel_all`."""

  async def cancel_all(self) -> CancelAllResult:
    """Cancels all open orders on the account, including untriggered orders and orders resting in the book. The details of each individual cancelled order are also streamed on the `executions` channel.

    References:
      - [Official docs](https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/cancel_all)
    """
    return await self.request('cancel_all', validator=validate_cancel_all)
