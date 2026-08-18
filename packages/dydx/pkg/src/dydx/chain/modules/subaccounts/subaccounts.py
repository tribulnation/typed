"""SubaccountAll -- Query all subaccounts."""

from typed_core import PaginatedResponse
from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.subaccounts as subaccounts_proto
from dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from dydx.protos.dydxprotocol.subaccounts import Subaccount


class Subaccounts(GrpcEndpoint):
  """Query all subaccounts."""

  @wrap_exceptions
  async def subaccounts(
    self,
    pagination: PageRequest | None = None,
  ) -> subaccounts_proto.QuerySubaccountAllResponse:
    """Query all subaccounts."""
    return await subaccounts_proto.QueryStub(self.channel).subaccount_all(
      subaccounts_proto.QueryAllSubaccountRequest(pagination=pagination)
    )

  def subaccounts_paged(
    self,
    limit: int | None = None,
  ) -> PaginatedResponse[Subaccount, bytes]:
    """Page through `subaccounts`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[Subaccount], bytes | None]:
      response = await self.subaccounts(
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0))
      )
      rows = response.subaccount
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
