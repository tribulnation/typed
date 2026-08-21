"""DelegationTotalRewards -- Query the total rewards accrued by a delegator across all validators."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.distribution.v1beta1 as v1beta1_proto


class DelegationTotalRewards(GrpcEndpoint):
  """Query the total rewards accrued by a delegator across all validators."""

  @wrap_exceptions
  async def delegation_total_rewards(
    self,
    delegator_address: str,
  ) -> v1beta1_proto.QueryDelegationTotalRewardsResponse:
    """Query the total rewards accrued by a delegator across all validators."""
    return await v1beta1_proto.QueryStub(self.channel).delegation_total_rewards(
      v1beta1_proto.QueryDelegationTotalRewardsRequest(
        delegator_address=delegator_address
      )
    )
