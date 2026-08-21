"""Validators -- Query all validators that match a given status."""

from typed_core import PaginatedResponse
from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.staking.v1beta1 as v1beta1_proto
from typed_dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from typed_dydx.protos.cosmos.staking.v1beta1 import Validator


class Validators(GrpcEndpoint):
  """Query all validators that match a given status."""

  @wrap_exceptions
  async def validators(
    self,
    status: str,
    *,
    pagination: PageRequest | None = None,
  ) -> v1beta1_proto.QueryValidatorsResponse:
    """Query all validators that match a given status."""
    return await v1beta1_proto.QueryStub(self.channel).validators(
      v1beta1_proto.QueryValidatorsRequest(status=status, pagination=pagination)
    )

  def validators_paged(
    self,
    status: str,
    *,
    limit: int | None = None,
  ) -> PaginatedResponse[Validator, bytes]:
    """Page through `validators`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[Validator], bytes | None]:
      response = await self.validators(
        status,
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0)),
      )
      rows = response.validators
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
