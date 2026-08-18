"""KuCoin Debit endpoints."""

from .borrow import Borrow
from .borrow_history import BorrowHistory
from .borrow_interest_rate import BorrowInterestRate
from .interest_history import InterestHistory
from .modify_leverage import ModifyLeverage
from .repay import Repay
from .repay_history import RepayHistory


class Debit(
  Borrow,
  BorrowHistory,
  BorrowInterestRate,
  InterestHistory,
  ModifyLeverage,
  Repay,
  RepayHistory,
):
  """KuCoin Debit endpoints."""
