"""Simulate -- Simulate executing a transaction to estimate the gas it would consume."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.tx.v1beta1 as v1beta1_proto
from typed_dydx.protos.cosmos.tx.v1beta1 import Tx


class Simulate(GrpcEndpoint):
  """Simulate executing a transaction to estimate the gas it would consume."""

  @wrap_exceptions
  async def simulate(
    self,
    tx: Tx | None = None,
    *,
    tx_bytes: bytes,
  ) -> v1beta1_proto.SimulateResponse:
    """Simulate executing a transaction to estimate the gas it would consume."""
    return await v1beta1_proto.ServiceStub(self.channel).simulate(
      v1beta1_proto.SimulateRequest(tx=tx, tx_bytes=tx_bytes)
    )
