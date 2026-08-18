"""GetTx -- Query a transaction by its hex-encoded hash."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.cosmos.tx.v1beta1 as v1beta1_proto


class GetTx(GrpcEndpoint):
  """Query a transaction by its hex-encoded hash."""

  @wrap_exceptions
  async def get_tx(self, hash: str) -> v1beta1_proto.GetTxResponse:
    """Query a transaction by its hex-encoded hash."""
    return await v1beta1_proto.ServiceStub(self.channel).get_tx(
      v1beta1_proto.GetTxRequest(hash=hash)
    )
