"""Perpetual -- Query a perpetual by id."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.perpetuals as perpetuals_proto


class Perpetual(GrpcEndpoint):
  """Query a perpetual by id."""

  @wrap_exceptions
  async def perpetual(self, id: int) -> perpetuals_proto.QueryPerpetualResponse:
    """Query a perpetual by id."""
    return await perpetuals_proto.QueryStub(self.channel).perpetual(
      perpetuals_proto.QueryPerpetualRequest(id=id)
    )
