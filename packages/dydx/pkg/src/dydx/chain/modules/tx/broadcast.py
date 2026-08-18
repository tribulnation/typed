"""Cosmos tx broadcast query."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
from dydx.protos.cosmos.tx import v1beta1 as tx_proto

class Broadcast(GrpcEndpoint):
  """Transaction broadcast endpoint."""

  @wrap_exceptions
  async def broadcast(
    self,
    tx_bytes: bytes,
    *,
    mode: tx_proto.BroadcastMode = tx_proto.BroadcastMode.SYNC,
  ) -> tx_proto.BroadcastTxResponse:
    """Broadcast encoded transaction bytes."""
    request = tx_proto.BroadcastTxRequest(tx_bytes=tx_bytes, mode=mode)
    return await tx_proto.ServiceStub(self.channel).broadcast_tx(request)
