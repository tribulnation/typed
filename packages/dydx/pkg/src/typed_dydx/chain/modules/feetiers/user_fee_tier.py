"""UserFeeTier -- Query the fee tier for a user address."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.feetiers as feetiers_proto


class UserFeeTier(GrpcEndpoint):
  """Query the fee tier for a user address."""

  @wrap_exceptions
  async def user_fee_tier(self, user: str) -> feetiers_proto.QueryUserFeeTierResponse:
    """Query the fee tier for a user address."""
    return await feetiers_proto.QueryStub(self.channel).user_fee_tier(
      feetiers_proto.QueryUserFeeTierRequest(user=user)
    )
