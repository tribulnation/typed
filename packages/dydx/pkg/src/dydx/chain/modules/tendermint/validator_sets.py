"""Cosmos Tendermint latest validator set query."""

from typed_core import PaginatedResponse

from dydx.chain.core import GrpcEndpoint, wrap_exceptions
from dydx.chain.pagination import next_key, page_request
from dydx.protos.cosmos.base.query import v1beta1 as query_proto
from dydx.protos.cosmos.base.tendermint import v1beta1 as tendermint_proto

class ValidatorSets(GrpcEndpoint):
  """Tendermint latest validator set endpoint."""

  @wrap_exceptions
  async def get_latest_validator_set(
    self, *, pagination: query_proto.PageRequest | None = None,
  ) -> tendermint_proto.GetLatestValidatorSetResponse:
    """Query the latest validator set."""
    request = tendermint_proto.GetLatestValidatorSetRequest(pagination=pagination)
    return await tendermint_proto.ServiceStub(self.channel).get_latest_validator_set(request)

  def get_latest_validator_set_paged(
    self, *, limit: int | None = None,
  ) -> PaginatedResponse[tendermint_proto.Validator, bytes]:
    """Page through the latest validator set.

    Args:
      limit: Optional maximum number of validators per page.

    Returns:
      A paginated response yielding validator pages.
    """
    async def next(key: bytes) -> tuple[list[tendermint_proto.Validator], bytes | None]:
      """Fetch the next latest validator-set page."""
      response = await self.get_latest_validator_set(
        pagination=page_request(key, limit=limit),
      )
      return response.validators, next_key(response)

    return PaginatedResponse(b'', next)
