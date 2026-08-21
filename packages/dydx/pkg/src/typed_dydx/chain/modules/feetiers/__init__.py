from .perpetual_fee_params import PerpetualFeeParams
from .user_fee_tier import UserFeeTier
from .user_staking_tier import UserStakingTier

from typed_dydx.chain.core import GrpcEndpoint


class Feetiers(
  PerpetualFeeParams,
  UserFeeTier,
  UserStakingTier,
  GrpcEndpoint,
):
  """Feetiers endpoints."""
