"""UserStakingTier -- Query a user's current staked amount and staking fee tier."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.dydxprotocol.feetiers as feetiers_proto


class UserStakingTier(GrpcEndpoint):
  """Query a user's current staked amount and staking fee tier."""

  @wrap_exceptions
  async def user_staking_tier(
    self,
    address: str,
  ) -> feetiers_proto.QueryUserStakingTierResponse:
    """Query a user's current staked amount and staking fee tier."""
    return await feetiers_proto.QueryStub(self.channel).user_staking_tier(
      feetiers_proto.QueryUserStakingTierRequest(address=address)
    )
