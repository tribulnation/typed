"""Account -- Query account details based on address."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.auth.v1beta1 as v1beta1_proto


class Account(GrpcEndpoint):
  """Query account details based on address."""

  @wrap_exceptions
  async def account(self, address: str) -> v1beta1_proto.QueryAccountResponse:
    """Query account details based on address."""
    return await v1beta1_proto.QueryStub(self.channel).account(
      v1beta1_proto.QueryAccountRequest(address=address)
    )
