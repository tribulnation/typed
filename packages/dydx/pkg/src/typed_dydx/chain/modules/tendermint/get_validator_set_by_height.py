"""GetValidatorSetByHeight -- Query the validator set at a given height."""

from typed_core import PaginatedResponse
from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.base.tendermint.v1beta1 as v1beta1_proto
from typed_dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from typed_dydx.protos.cosmos.base.tendermint.v1beta1 import Validator


class GetValidatorSetByHeight(GrpcEndpoint):
  """Query the validator set at a given height."""

  @wrap_exceptions
  async def get_validator_set_by_height(
    self,
    height: int,
    *,
    pagination: PageRequest | None = None,
  ) -> v1beta1_proto.GetValidatorSetByHeightResponse:
    """Query the validator set at a given height."""
    return await v1beta1_proto.ServiceStub(self.channel).get_validator_set_by_height(
      v1beta1_proto.GetValidatorSetByHeightRequest(height=height, pagination=pagination)
    )

  def get_validator_set_by_height_paged(
    self,
    height: int,
    *,
    limit: int | None = None,
  ) -> PaginatedResponse[Validator, bytes]:
    """Page through `get_validator_set_by_height`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[Validator], bytes | None]:
      response = await self.get_validator_set_by_height(
        height,
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0)),
      )
      rows = response.validators
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
