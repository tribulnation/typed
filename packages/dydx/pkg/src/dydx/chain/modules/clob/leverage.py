"""Leverage -- Query leverage info for a subaccount."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.clob as clob_proto


class Leverage(GrpcEndpoint):
  """Query leverage info for a subaccount."""

  @wrap_exceptions
  async def leverage(
    self, owner: str, *, number: int
  ) -> clob_proto.QueryLeverageResponse:
    """Query leverage info for a subaccount."""
    return await clob_proto.QueryStub(self.channel).leverage(
      clob_proto.QueryLeverageRequest(owner=owner, number=number)
    )
