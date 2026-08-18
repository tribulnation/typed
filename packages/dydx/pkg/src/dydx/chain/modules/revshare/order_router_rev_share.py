"""OrderRouterRevShare -- Query order router revenue share for an address."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.revshare as revshare_proto


class OrderRouterRevShare(GrpcEndpoint):
  """Query order router revenue share for an address."""

  @wrap_exceptions
  async def order_router_rev_share(
    self,
    address: str,
  ) -> revshare_proto.QueryOrderRouterRevShareResponse:
    """Query order router revenue share for an address."""
    return await revshare_proto.QueryStub(self.channel).order_router_rev_share(
      revshare_proto.QueryOrderRouterRevShare(address=address)
    )
