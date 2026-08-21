"""AllAssets -- Query all assets."""

from typed_core import PaginatedResponse
from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.assets as assets_proto
from typed_dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from typed_dydx.protos.dydxprotocol.assets import Asset


class Assets(GrpcEndpoint):
  """Query all assets."""

  @wrap_exceptions
  async def assets(
    self,
    pagination: PageRequest | None = None,
  ) -> assets_proto.QueryAllAssetsResponse:
    """Query all assets."""
    return await assets_proto.QueryStub(self.channel).all_assets(
      assets_proto.QueryAllAssetsRequest(pagination=pagination)
    )

  def assets_paged(self, limit: int | None = None) -> PaginatedResponse[Asset, bytes]:
    """Page through `assets`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[Asset], bytes | None]:
      response = await self.assets(
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0))
      )
      rows = response.asset
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
