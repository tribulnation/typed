from .cancel_withdrawal import CancelWithdrawal
from .get_withdrawals import GetWithdrawals
from .withdraw import Withdraw


class Withdrawals(
  CancelWithdrawal,
  GetWithdrawals,
  Withdraw,
):
  """Withdrawals endpoints."""
