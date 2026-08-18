"""dYdX batch order cancellation helper."""

from collections import defaultdict
from dataclasses import dataclass

from typed_core.exceptions import BadRequest
from typing_extensions import Sequence

from dydx.node.constants import SHORT_BLOCK_WINDOW
from dydx.node.context import NodeContext
from dydx.node.tx import Tx
from dydx.protos.cosmos.tx import v1beta1 as tx_proto
from dydx.protos.dydxprotocol import clob

@dataclass
class BatchCancelOrders:
  """Batch order cancellation endpoint."""

  context: NodeContext
  """Shared node context used for wallet and chain access."""
  tx: Tx
  """Transaction helper used for signing and broadcasting."""

  async def batch_cancel_orders(
    self,
    order_ids: Sequence[clob.OrderId],
    *,
    good_til_block: int | None = None,
    mode: tx_proto.BroadcastMode = tx_proto.BroadcastMode(2),
    simulate: bool = False,
  ) -> tx_proto.BroadcastTxResponse:
    """Build, sign, and broadcast short-term order cancellations.

    Args:
      order_ids: Short-term order identifiers to cancel. All must belong to
        the same subaccount.
      good_til_block: Optional cancellation expiry block. Loaded from the
        latest chain block when omitted.
      mode: Cosmos broadcast mode.
      simulate: Whether to simulate the transaction before broadcasting.

    Returns:
      Cosmos broadcast response.

    Raises:
      BadRequest: Raised when no orders are provided, orders are not short-term,
        orders belong to different subaccounts, or latest block metadata is
        unavailable.
    """
    if not order_ids:
      raise BadRequest('At least one order ID is required')
    subaccount_id = order_ids[0].subaccount_id
    if subaccount_id is None:
      raise BadRequest('Order IDs must include a subaccount ID')
    orders_by_pair: dict[int, list[int]] = defaultdict(list)
    for order_id in order_ids:
      if order_id.order_flags != 0:
        raise BadRequest('Only short-term orders can be canceled in a batch')
      if order_id.subaccount_id != subaccount_id:
        raise BadRequest('All batch-canceled orders must use the same subaccount')
      orders_by_pair[order_id.clob_pair_id].append(order_id.client_id)
    if good_til_block is None:
      latest_block = await self.context.chain.tendermint.get_latest_block()
      block = latest_block.block
      if block is None or block.header is None:
        raise BadRequest('Latest block response did not include a block header')
      good_til_block = block.header.height + SHORT_BLOCK_WINDOW
    message = clob.MsgBatchCancel(
      subaccount_id=subaccount_id,
      short_term_cancels=[
        clob.OrderBatch(clob_pair_id=clob_pair_id, client_ids=client_ids)
        for clob_pair_id, client_ids in orders_by_pair.items()
      ],
      good_til_block=good_til_block,
    )
    return await self.tx.sign_and_broadcast([message], mode=mode, simulate=simulate)
