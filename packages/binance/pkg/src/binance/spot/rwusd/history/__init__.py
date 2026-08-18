from .rate_history import RateHistory
from .redemption_history import RedemptionHistory
from .rewards_history import RewardsHistory
from .subscription_history import SubscriptionHistory


class History(RateHistory, RedemptionHistory, RewardsHistory, SubscriptionHistory):
  """Binance history endpoints."""
