"""DelegatorDelegations -- Query all delegations of a given delegator address."""

from typed_core import PaginatedResponse
from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.staking.v1beta1 as v1beta1_proto
from typed_dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from typed_dydx.protos.cosmos.staking.v1beta1 import DelegationResponse


class DelegatorDelegations(GrpcEndpoint):
  """Query all delegations of a given delegator address."""

  @wrap_exceptions
  async def delegator_delegations(
    self,
    delegator_addr: str,
    *,
    pagination: PageRequest | None = None,
  ) -> v1beta1_proto.QueryDelegatorDelegationsResponse:
    """Query all delegations of a given delegator address."""
    return await v1beta1_proto.QueryStub(self.channel).delegator_delegations(
      v1beta1_proto.QueryDelegatorDelegationsRequest(
        delegator_addr=delegator_addr, pagination=pagination
      )
    )

  def delegator_delegations_paged(
    self,
    delegator_addr: str,
    *,
    limit: int | None = None,
  ) -> PaginatedResponse[DelegationResponse, bytes]:
    """Page through `delegator_delegations`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[DelegationResponse], bytes | None]:
      response = await self.delegator_delegations(
        delegator_addr,
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0)),
      )
      rows = response.delegation_responses
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
