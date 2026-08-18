"""AllLiquidityTiers -- Query all liquidity tiers."""

from typed_core import PaginatedResponse
from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.perpetuals as perpetuals_proto
from dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from dydx.protos.dydxprotocol.perpetuals import LiquidityTier


class LiquidityTiers(GrpcEndpoint):
  """Query all liquidity tiers."""

  @wrap_exceptions
  async def liquidity_tiers(
    self,
    pagination: PageRequest | None = None,
  ) -> perpetuals_proto.QueryAllLiquidityTiersResponse:
    """Query all liquidity tiers."""
    return await perpetuals_proto.QueryStub(self.channel).all_liquidity_tiers(
      perpetuals_proto.QueryAllLiquidityTiersRequest(pagination=pagination)
    )

  def liquidity_tiers_paged(
    self,
    limit: int | None = None,
  ) -> PaginatedResponse[LiquidityTier, bytes]:
    """Page through `liquidity_tiers`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[LiquidityTier], bytes | None]:
      response = await self.liquidity_tiers(
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0))
      )
      rows = response.liquidity_tiers
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
