"""GetLatestBlock -- Query the latest committed block."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.cosmos.base.tendermint.v1beta1 as v1beta1_proto


class GetLatestBlock(GrpcEndpoint):
  """Query the latest committed block."""

  @wrap_exceptions
  async def get_latest_block(self) -> v1beta1_proto.GetLatestBlockResponse:
    """Query the latest committed block."""
    return await v1beta1_proto.ServiceStub(self.channel).get_latest_block(
      v1beta1_proto.GetLatestBlockRequest()
    )
