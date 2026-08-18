"""dYdX order cancellation helper."""

from dataclasses import dataclass

from typed_core.exceptions import BadRequest

from dydx.node.constants import SHORT_BLOCK_WINDOW, STATEFUL_ORDER_TIME_WINDOW
from dydx.node.context import NodeContext
from dydx.node.tx import Tx
from dydx.protos.cosmos.tx import v1beta1 as tx_proto
from dydx.protos.dydxprotocol import clob

@dataclass
class CancelOrder:
  """Order cancellation endpoint."""

  context: NodeContext
  """Shared node context used for wallet and chain access."""
  tx: Tx
  """Transaction helper used for signing and broadcasting."""

  async def cancel_order(
    self,
    order_id: clob.OrderId,
    *,
    good_til_block: int | None = None,
    good_til_block_time: int | None = None,
    mode: tx_proto.BroadcastMode = tx_proto.BroadcastMode.SYNC,
    simulate: bool = False,
  ) -> tx_proto.BroadcastTxResponse:
    """Build, sign, and broadcast an order cancellation.

    Args:
      order_id: Protocol order identifier to cancel.
      good_til_block: Optional short-term cancellation expiry block. Loaded
        from the latest chain block when omitted for short-term orders.
      good_til_block_time: Optional stateful cancellation expiry timestamp.
        Loaded from the latest chain block time when omitted for stateful
        orders.
      mode: Cosmos broadcast mode.
      simulate: Whether to simulate the transaction before broadcasting.

    Returns:
      Cosmos broadcast response.

    Raises:
      BadRequest: Raised when latest block metadata needed for default expiry
        is unavailable.
    """
    if good_til_block is None and good_til_block_time is None:
      latest_block = await self.context.chain.tendermint.get_latest_block()
      block = latest_block.block
      if block is None or block.header is None:
        raise BadRequest('Latest block response did not include a block header')
      if order_id.order_flags == 0:
        good_til_block = block.header.height + SHORT_BLOCK_WINDOW
      else:
        if block.header.time is None:
          raise BadRequest('Latest block response did not include block time')
        good_til_block_time = int(block.header.time.timestamp()) + STATEFUL_ORDER_TIME_WINDOW
    message = clob.MsgCancelOrder(
      order_id=order_id,
      good_til_block=good_til_block,
      good_til_block_time=good_til_block_time,
    )
    return await self.tx.sign_and_broadcast([message], mode=mode, simulate=simulate)
