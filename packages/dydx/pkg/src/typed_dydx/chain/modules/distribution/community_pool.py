"""CommunityPool -- Query the amount of coins in the community pool."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.distribution.v1beta1 as v1beta1_proto


class CommunityPool(GrpcEndpoint):
  """Query the amount of coins in the community pool."""

  @wrap_exceptions
  async def community_pool(self) -> v1beta1_proto.QueryCommunityPoolResponse:
    """Query the amount of coins in the community pool."""
    return await v1beta1_proto.QueryStub(self.channel).community_pool(
      v1beta1_proto.QueryCommunityPoolRequest()
    )
