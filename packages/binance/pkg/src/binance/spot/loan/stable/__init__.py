from .borrow_history import BorrowHistory
from .income_history import IncomeHistory
from .ltv_adjustment_history import LtvAdjustmentHistory
from .repayment_history import RepaymentHistory


class Stable(BorrowHistory, IncomeHistory, LtvAdjustmentHistory, RepaymentHistory):
  """Binance stable endpoints."""
