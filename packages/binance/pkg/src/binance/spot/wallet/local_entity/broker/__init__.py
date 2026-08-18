from .deposit_provide_info import DepositProvideInfo
from .withdraw_apply import WithdrawApply


class Broker(DepositProvideInfo, WithdrawApply):
  """Binance broker endpoints."""
