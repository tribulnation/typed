"""`streams.trading.batch_cancel` -- WebSocket trading method."""

from datetime import datetime
from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.ws_rpc import WsRpcEndpoint


class BatchCancelReply(TypedDict):
  """Reply to a `batch_cancel` request -- the count lives directly on the frame, not under a `result` key."""

  method: Literal['batch_cancel']
  """Echoes the request method, `batch_cancel`."""
  req_id: int
  """Echoes the request's correlation id."""
  success: bool
  """`true` on a successful cancellation."""
  orders_cancelled: NotRequired[int]
  """Number of orders cancelled. Confirmed live -- upstream's docs page instead describes a nested `result: {count, warnings}` shape, which the real reply does not send; see `notes`."""
  warnings: NotRequired[list[str]]
  """Non-fatal warnings about the cancellation, if any. Documented by upstream nested under `result`; kept top-level here to match the real reply's flat shape, unconfirmed live (none appeared in this run's capture)."""
  time_in: NotRequired[datetime]
  """Server receive timestamp."""
  time_out: NotRequired[datetime]
  """Server response timestamp."""


validate_batch_cancel = validator(BatchCancelReply)


class BatchCancel(WsRpcEndpoint):
  """`streams.trading.batch_cancel`."""

  async def batch_cancel(
    self,
    *,
    orders: list[str],
    cl_ord_id: list[str] | None = None,
  ) -> BatchCancelReply:
    """Cancels multiple orders (minimum 2, maximum 50) in a single request, identified by a mix of client or Kraken identifiers.

    Args:
      orders: List containing either client `order_userref` or Kraken `order_id` identifiers, 2 to 50 of them.
      cl_ord_id: List of client `cl_ord_id` identifiers.

    References:
      - [Official docs](https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/batch_cancel)
    """
    params: dict = {
      'orders': orders,
    }
    if cl_ord_id is not None:
      params['cl_ord_id'] = cl_ord_id

    return await self.raw_request(
      'batch_cancel', params, validator=validate_batch_cancel
    )
