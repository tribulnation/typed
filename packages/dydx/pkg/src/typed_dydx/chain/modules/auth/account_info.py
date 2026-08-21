"""AccountInfo -- Query account info which is common to all account types."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.auth.v1beta1 as v1beta1_proto


class AccountInfo(GrpcEndpoint):
  """Query account info which is common to all account types."""

  @wrap_exceptions
  async def account_info(self, address: str) -> v1beta1_proto.QueryAccountInfoResponse:
    """Query account info which is common to all account types."""
    return await v1beta1_proto.QueryStub(self.channel).account_info(
      v1beta1_proto.QueryAccountInfoRequest(address=address)
    )
