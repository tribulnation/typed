from .bnsol_rewards_history import BnsolRewardsHistory
from .boost_rewards_history import BoostRewardsHistory
from .rate_history import RateHistory
from .redemption_history import RedemptionHistory
from .staking_history import StakingHistory
from .unclaimed_rewards import UnclaimedRewards


class History(
  BnsolRewardsHistory,
  BoostRewardsHistory,
  RateHistory,
  RedemptionHistory,
  StakingHistory,
  UnclaimedRewards,
):
  """Binance history endpoints."""
