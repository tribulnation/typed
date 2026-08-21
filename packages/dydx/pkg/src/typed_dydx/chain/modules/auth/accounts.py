"""Accounts -- Query all existing accounts."""

from typed_core import PaginatedResponse
from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.auth.v1beta1 as v1beta1_proto
from typed_dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from typed_dydx.protos.google.protobuf import Any


class Accounts(GrpcEndpoint):
  """Query all existing accounts."""

  @wrap_exceptions
  async def accounts(
    self,
    pagination: PageRequest | None = None,
  ) -> v1beta1_proto.QueryAccountsResponse:
    """Query all existing accounts."""
    return await v1beta1_proto.QueryStub(self.channel).accounts(
      v1beta1_proto.QueryAccountsRequest(pagination=pagination)
    )

  def accounts_paged(self, limit: int | None = None) -> PaginatedResponse[Any, bytes]:
    """Page through `accounts`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[Any], bytes | None]:
      response = await self.accounts(
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0))
      )
      rows = response.accounts
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
