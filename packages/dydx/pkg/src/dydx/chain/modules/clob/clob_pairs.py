"""ClobPairAll -- Query all CLOB pairs."""

from typed_core import PaginatedResponse
from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.dydxprotocol.clob as clob_proto
from dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from dydx.protos.dydxprotocol.clob import ClobPair


class ClobPairs(GrpcEndpoint):
  """Query all CLOB pairs."""

  @wrap_exceptions
  async def clob_pairs(
    self,
    pagination: PageRequest | None = None,
  ) -> clob_proto.QueryClobPairAllResponse:
    """Query all CLOB pairs."""
    return await clob_proto.QueryStub(self.channel).clob_pair_all(
      clob_proto.QueryAllClobPairRequest(pagination=pagination)
    )

  def clob_pairs_paged(
    self,
    limit: int | None = None,
  ) -> PaginatedResponse[ClobPair, bytes]:
    """Page through `clob_pairs`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[ClobPair], bytes | None]:
      response = await self.clob_pairs(
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0))
      )
      rows = response.clob_pair
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
