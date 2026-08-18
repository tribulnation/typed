"""MarketPrice -- Query a market price by id."""

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.prices as prices_proto


class MarketPrice(GrpcEndpoint):
  """Query a market price by id."""

  @wrap_exceptions
  async def market_price(self, id: int) -> prices_proto.QueryMarketPriceResponse:
    """Query a market price by id."""
    return await prices_proto.QueryStub(self.channel).market_price(
      prices_proto.QueryMarketPriceRequest(id=id)
    )
