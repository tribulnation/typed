"""MarketMapperRevShareDetails -- Query market mapper revenue share details for a specific market."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.revshare as revshare_proto


class MarketMapperRevShareDetails(GrpcEndpoint):
  """Query market mapper revenue share details for a specific market."""

  @wrap_exceptions
  async def market_mapper_rev_share_details(
    self,
    market_id: int,
  ) -> revshare_proto.QueryMarketMapperRevShareDetailsResponse:
    """Query market mapper revenue share details for a specific market."""
    return await revshare_proto.QueryStub(self.channel).market_mapper_rev_share_details(
      revshare_proto.QueryMarketMapperRevShareDetails(market_id=market_id)
    )
