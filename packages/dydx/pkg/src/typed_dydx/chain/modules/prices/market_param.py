"""MarketParam -- Query a market parameter by id."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.prices as prices_proto


class MarketParam(GrpcEndpoint):
  """Query a market parameter by id."""

  @wrap_exceptions
  async def market_param(self, id: int) -> prices_proto.QueryMarketParamResponse:
    """Query a market parameter by id."""
    return await prices_proto.QueryStub(self.channel).market_param(
      prices_proto.QueryMarketParamRequest(id=id)
    )
