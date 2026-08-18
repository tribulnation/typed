from .cancel_withdraw import CancelWithdraw
from .convert_dust import ConvertDust
from .convertible_assets import ConvertibleAssets
from .currency_info import CurrencyInfo
from .deposit_address import DepositAddress
from .deposit_history import DepositHistory
from .dust_log import DustLog
from .generate_deposit_address import GenerateDepositAddress
from .internal_transfer import InternalTransfer
from .internal_transfer_history import InternalTransferHistory
from .universal_transfer import UniversalTransfer
from .universal_transfer_by_tran_id import UniversalTransferByTranId
from .universal_transfer_history import UniversalTransferHistory
from .withdraw import Withdraw
from .withdraw_address import WithdrawAddress
from .withdraw_apply import WithdrawApply
from .withdraw_history import WithdrawHistory

class Wallet(CancelWithdraw, ConvertDust, ConvertibleAssets, CurrencyInfo, DepositAddress, DepositHistory, DustLog, GenerateDepositAddress, InternalTransfer, InternalTransferHistory, UniversalTransfer, UniversalTransferByTranId, UniversalTransferHistory, Withdraw, WithdrawAddress, WithdrawApply, WithdrawHistory):
  ...
