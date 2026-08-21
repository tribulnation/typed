"""DelegationRewards -- Query the total rewards accrued by a delegation to one validator."""

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.distribution.v1beta1 as v1beta1_proto


class DelegationRewards(GrpcEndpoint):
  """Query the total rewards accrued by a delegation to one validator."""

  @wrap_exceptions
  async def delegation_rewards(
    self,
    *,
    delegator_address: str,
    validator_address: str,
  ) -> v1beta1_proto.QueryDelegationRewardsResponse:
    """Query the total rewards accrued by a delegation to one validator."""
    return await v1beta1_proto.QueryStub(self.channel).delegation_rewards(
      v1beta1_proto.QueryDelegationRewardsRequest(
        delegator_address=delegator_address, validator_address=validator_address
      )
    )
