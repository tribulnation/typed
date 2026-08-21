"""Params -- Query rewards module parameters."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.rewards as rewards_proto


class Params(GrpcEndpoint):
  """Query rewards module parameters."""

  @wrap_exceptions
  async def params(self) -> rewards_proto.QueryParamsResponse:
    """Query rewards module parameters."""
    return await rewards_proto.QueryStub(self.channel).params(
      rewards_proto.QueryParamsRequest()
    )
