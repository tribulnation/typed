"""Cosmos bank denoms metadata query."""

from typed_core import PaginatedResponse

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
from typed_dydx.chain.pagination import next_key, page_request
from typed_dydx.protos.cosmos.bank import v1beta1 as bank_proto
from typed_dydx.protos.cosmos.base.query import v1beta1 as query_proto

class DenomsMetadata(GrpcEndpoint):
  """Bank denoms metadata endpoint."""

  @wrap_exceptions
  async def denoms_metadata(
    self, *, pagination: query_proto.PageRequest | None = None,
  ) -> bank_proto.QueryDenomsMetadataResponse:
    """Query metadata for all registered denoms.

    Args:
      pagination: Optional page controls for large metadata registries.

    Returns:
      Metadata entries describing denom display units and exponents.
    """
    request = bank_proto.QueryDenomsMetadataRequest(pagination=pagination)
    return await bank_proto.QueryStub(self.channel).denoms_metadata(request)

  def denoms_metadata_paged(
    self, *, limit: int | None = None,
  ) -> PaginatedResponse[bank_proto.Metadata, bytes]:
    """Page through metadata for all registered denoms.

    Args:
      limit: Optional maximum number of metadata entries per page.

    Returns:
      A paginated response yielding denom metadata pages.
    """
    async def next(key: bytes) -> tuple[list[bank_proto.Metadata], bytes | None]:
      """Fetch the next denom metadata page."""
      response = await self.denoms_metadata(pagination=page_request(key, limit=limit))
      return response.metadatas, next_key(response)

    return PaginatedResponse(b'', next)
