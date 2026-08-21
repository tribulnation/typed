"""`classic_streams.cancel_order` -- hand-written, not codegen'd; see `place_order.py`'s
module docstring for why (same reason: `id` is connection-managed, not caller-facing).
"""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator

from ...core.endpoint.stream import StreamEndpoint

InstType = Literal['SPOT', 'USDT-FUTURES', 'COIN-FUTURES', 'USDC-FUTURES']


class CancelOrderParams(TypedDict):
  """Order-cancellation parameters; identical shape for spot and mix."""

  orderId: NotRequired[str]
  """Order ID to cancel. Either `orderId` or `clientOid` is required; if both are
  given, `orderId` wins.
  """
  clientOid: NotRequired[str]
  """Custom order ID to cancel. Either `orderId` or `clientOid` is required; if both
  are given, `orderId` wins.
  """


class CancelOrderReplyArg(TypedDict):
  """One echoed command result."""

  id: str
  """Echoed command identifier."""
  instType: InstType
  """Product line type."""
  channel: Literal['cancel-order']
  """Command name."""
  instId: str
  """Product ID."""
  params: CancelOrderParams
  """Order-cancellation parameters; identical shape for spot and mix."""


class CancelOrderReply(TypedDict):
  """Reply to the `cancel-order` command -- the one answering frame."""

  event: Literal['trade', 'error']
  """Event name: `trade` on success, `error` on failure."""
  arg: list[CancelOrderReplyArg]
  """Echoed command result(s)."""
  code: str | int
  """Result code; docs show `0` (integer) on success."""
  msg: str
  """Result message, e.g. `"Success"`."""


class CancelOrder(StreamEndpoint):
  """`classic_streams.cancel_order`."""

  async def cancel_order(
    self, inst_type: InstType, inst_id: str, params: CancelOrderParams,
  ) -> CancelOrderReply:
    """Cancel a single spot or mix order over the private WebSocket connection.
    Requires the `login` handshake first (automatic, on first authed call on this
    connection).

    Args:
      inst_type: Product line type: `SPOT`, or a futures product type
        (`USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`).
      inst_id: Product ID, e.g. `BTCUSDT`.
      params: Order-cancellation parameters; identical shape for spot and mix.

    References:
      - [Official docs](https://www.bitget.com/api-doc/classic/spot/websocket/private/Cancel-Order-Channel)
    """
    req = {
      'op': 'trade',
      'args': [
        {
          'instType': inst_type,
          'instId': inst_id,
          'channel': 'cancel-order',
          'params': params,
        }
      ],
    }
    return await self.authed_command(req, validator=validator(CancelOrderReply))
