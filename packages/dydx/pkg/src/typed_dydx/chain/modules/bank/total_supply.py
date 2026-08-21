"""Cosmos bank total supply query."""

from typed_core import PaginatedResponse

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
from typed_dydx.chain.pagination import next_key, page_request
from typed_dydx.protos.cosmos.bank import v1beta1 as bank_proto
from typed_dydx.protos.cosmos.base import v1beta1 as coin_proto
from typed_dydx.protos.cosmos.base.query import v1beta1 as query_proto

class TotalSupply(GrpcEndpoint):
  """Bank total supply endpoint."""

  @wrap_exceptions
  async def total_supply(
    self, *, pagination: query_proto.PageRequest | None = None,
  ) -> bank_proto.QueryTotalSupplyResponse:
    """Query total token supply."""
    request = bank_proto.QueryTotalSupplyRequest(pagination=pagination)
    return await bank_proto.QueryStub(self.channel).total_supply(request)

  def total_supply_paged(self, *, limit: int | None = None) -> PaginatedResponse[coin_proto.Coin, bytes]:
    """Page through total token supply.

    Args:
      limit: Optional maximum number of supply entries per page.

    Returns:
      A paginated response yielding supply pages.
    """
    async def next(key: bytes) -> tuple[list[coin_proto.Coin], bytes | None]:
      """Fetch the next supply page."""
      response = await self.total_supply(pagination=page_request(key, limit=limit))
      return response.supply, next_key(response)

    return PaginatedResponse(b'', next)
