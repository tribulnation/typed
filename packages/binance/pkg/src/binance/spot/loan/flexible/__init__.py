from .adjust_ltv import AdjustLtv
from .borrow import Borrow
from .borrow_history import BorrowHistory
from .collateral_data import CollateralData
from .collateral_repay_rate import CollateralRepayRate
from .interest_rate_history import InterestRateHistory
from .liquidation_history import LiquidationHistory
from .loanable_data import LoanableData
from .ltv_adjustment_history import LtvAdjustmentHistory
from .ongoing_orders import OngoingOrders
from .repay import Repay
from .repayment_history import RepaymentHistory


class Flexible(
  AdjustLtv,
  Borrow,
  BorrowHistory,
  CollateralData,
  CollateralRepayRate,
  InterestRateHistory,
  LiquidationHistory,
  LoanableData,
  LtvAdjustmentHistory,
  OngoingOrders,
  Repay,
  RepaymentHistory,
):
  """Binance flexible endpoints."""
