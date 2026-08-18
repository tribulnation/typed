"""GetBlockByHeight -- Query the committed block for a given height."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.cosmos.base.tendermint.v1beta1 as v1beta1_proto


class GetBlockByHeight(GrpcEndpoint):
  """Query the committed block for a given height."""

  @wrap_exceptions
  async def get_block_by_height(
    self,
    height: int,
  ) -> v1beta1_proto.GetBlockByHeightResponse:
    """Query the committed block for a given height."""
    return await v1beta1_proto.ServiceStub(self.channel).get_block_by_height(
      v1beta1_proto.GetBlockByHeightRequest(height=height)
    )
