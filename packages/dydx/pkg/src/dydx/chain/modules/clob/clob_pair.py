"""ClobPair -- Query a CLOB pair by id."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.clob as clob_proto


class ClobPair(GrpcEndpoint):
  """Query a CLOB pair by id."""

  @wrap_exceptions
  async def clob_pair(self, id: int) -> clob_proto.QueryClobPairResponse:
    """Query a CLOB pair by id."""
    return await clob_proto.QueryStub(self.channel).clob_pair(
      clob_proto.QueryGetClobPairRequest(id=id)
    )
