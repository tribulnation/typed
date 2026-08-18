from .accrued_interest import AccruedInterest
from .application_status import ApplicationStatus
from .borrow import Borrow
from .borrow_interest_rate import BorrowInterestRate
from .collateral_account import CollateralAccount
from .collateral_data import CollateralData
from .fixed_rate_borrow import FixedRateBorrow
from .fixed_rate_market import FixedRateMarket
from .interest_rate_history import InterestRateHistory
from .loanable_data import LoanableData
from .ongoing_orders import OngoingOrders
from .renew import Renew
from .repay import Repay
from .repayment_history import RepaymentHistory


class Vip(
  AccruedInterest,
  ApplicationStatus,
  Borrow,
  BorrowInterestRate,
  CollateralAccount,
  CollateralData,
  FixedRateBorrow,
  FixedRateMarket,
  InterestRateHistory,
  LoanableData,
  OngoingOrders,
  Renew,
  Repay,
  RepaymentHistory,
):
  """Binance vip endpoints."""
