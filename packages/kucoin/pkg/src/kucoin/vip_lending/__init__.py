"""KuCoin VipLending endpoints."""

from .accounts import Accounts
from .discount_rate_configs import DiscountRateConfigs
from .loan_info import LoanInfoEndpoint


class VipLending(Accounts, DiscountRateConfigs, LoanInfoEndpoint):
  """KuCoin VipLending endpoints."""
