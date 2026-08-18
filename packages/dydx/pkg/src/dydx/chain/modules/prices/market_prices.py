"""AllMarketPrices -- Query all market prices."""

from typed_core import PaginatedResponse
from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.prices as prices_proto
from dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from dydx.protos.dydxprotocol.prices import MarketPrice


class MarketPrices(GrpcEndpoint):
  """Query all market prices."""

  @wrap_exceptions
  async def market_prices(
    self,
    pagination: PageRequest | None = None,
  ) -> prices_proto.QueryAllMarketPricesResponse:
    """Query all market prices."""
    return await prices_proto.QueryStub(self.channel).all_market_prices(
      prices_proto.QueryAllMarketPricesRequest(pagination=pagination)
    )

  def market_prices_paged(
    self,
    limit: int | None = None,
  ) -> PaginatedResponse[MarketPrice, bytes]:
    """Page through `market_prices`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[MarketPrice], bytes | None]:
      response = await self.market_prices(
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0))
      )
      rows = response.market_prices
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
