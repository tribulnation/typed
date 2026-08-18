"""AllPerpetuals -- Query all perpetuals."""

from typed_core import PaginatedResponse
from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.perpetuals as perpetuals_proto
from dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from dydx.protos.dydxprotocol.perpetuals import Perpetual


class Perpetuals(GrpcEndpoint):
  """Query all perpetuals."""

  @wrap_exceptions
  async def perpetuals(
    self,
    pagination: PageRequest | None = None,
  ) -> perpetuals_proto.QueryAllPerpetualsResponse:
    """Query all perpetuals."""
    return await perpetuals_proto.QueryStub(self.channel).all_perpetuals(
      perpetuals_proto.QueryAllPerpetualsRequest(pagination=pagination)
    )

  def perpetuals_paged(
    self,
    limit: int | None = None,
  ) -> PaginatedResponse[Perpetual, bytes]:
    """Page through `perpetuals`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[Perpetual], bytes | None]:
      response = await self.perpetuals(
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0))
      )
      rows = response.perpetual
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
