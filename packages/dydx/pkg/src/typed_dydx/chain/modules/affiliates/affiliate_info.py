"""AffiliateInfo -- Query affiliate info for an address."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.affiliates as affiliates_proto


class AffiliateInfo(GrpcEndpoint):
  """Query affiliate info for an address."""

  @wrap_exceptions
  async def affiliate_info(
    self, address: str
  ) -> affiliates_proto.AffiliateInfoResponse:
    """Query affiliate info for an address."""
    return await affiliates_proto.QueryStub(self.channel).affiliate_info(
      affiliates_proto.AffiliateInfoRequest(address=address)
    )
