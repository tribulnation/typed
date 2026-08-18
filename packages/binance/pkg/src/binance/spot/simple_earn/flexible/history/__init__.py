from .collateral_record import CollateralRecord
from .rate_history import RateHistory
from .redemption_record import RedemptionRecord
from .rewards_history import RewardsHistory
from .subscription_record import SubscriptionRecord


class History(
  CollateralRecord, RateHistory, RedemptionRecord, RewardsHistory, SubscriptionRecord
):
  """Binance history endpoints."""
