"""Pool -- Query the bonded and not-bonded token pool state."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.cosmos.staking.v1beta1 as v1beta1_proto


class Pool(GrpcEndpoint):
  """Query the bonded and not-bonded token pool state."""

  @wrap_exceptions
  async def pool(self) -> v1beta1_proto.QueryPoolResponse:
    """Query the bonded and not-bonded token pool state."""
    return await v1beta1_proto.QueryStub(self.channel).pool(
      v1beta1_proto.QueryPoolRequest()
    )
