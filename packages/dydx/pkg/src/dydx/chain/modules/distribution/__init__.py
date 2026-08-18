from .community_pool import CommunityPool
from .delegation_rewards import DelegationRewards
from .delegation_total_rewards import DelegationTotalRewards

from dydx.chain.core import GrpcEndpoint


class Distribution(
  CommunityPool,
  DelegationRewards,
  DelegationTotalRewards,
  GrpcEndpoint,
):
  """Distribution endpoints."""
