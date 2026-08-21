"""GetNodeInfo -- Query the current node's info."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.base.tendermint.v1beta1 as v1beta1_proto


class GetNodeInfo(GrpcEndpoint):
  """Query the current node's info."""

  @wrap_exceptions
  async def get_node_info(self) -> v1beta1_proto.GetNodeInfoResponse:
    """Query the current node's info."""
    return await v1beta1_proto.ServiceStub(self.channel).get_node_info(
      v1beta1_proto.GetNodeInfoRequest()
    )
