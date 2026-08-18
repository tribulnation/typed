from .bnb_burn_status import BnbBurnStatus
from .change_sub_account_api_permission import ChangeSubAccountApiPermission
from .change_sub_account_coinm_futures_commission import (
  ChangeSubAccountCoinmFuturesCommission,
)
from .change_sub_account_commission import ChangeSubAccountCommission
from .change_sub_account_usdm_futures_commission import (
  ChangeSubAccountUsdmFuturesCommission,
)
from .commission_rebate_recent_record_futures import CommissionRebateRecentRecordFutures
from .commission_rebate_recent_record_spot import CommissionRebateRecentRecordSpot
from .create_sub_account import CreateSubAccount
from .create_sub_account_api_key import CreateSubAccountApiKey
from .delete_sub_account_api_ip_restriction import DeleteSubAccountApiIpRestriction
from .delete_sub_account_api_key import DeleteSubAccountApiKey
from .enable_bnb_burn_margin_interest import EnableBnbBurnMarginInterest
from .enable_bnb_burn_spot_margin import EnableBnbBurnSpotMargin
from .enable_sub_account_futures import EnableSubAccountFutures
from .enable_universal_transfer_permission import EnableUniversalTransferPermission
from .info import Info
from .sub_account import SubAccount
from .sub_account_api_ip_restriction import SubAccountApiIpRestriction
from .sub_account_api_key import SubAccountApiKey
from .sub_account_coinm_futures_commission import SubAccountCoinmFuturesCommission
from .sub_account_deposit_history import SubAccountDepositHistory
from .sub_account_futures_summary import SubAccountFuturesSummary
from .sub_account_futures_summary_v2 import SubAccountFuturesSummaryV2
from .sub_account_futures_summary_v3 import SubAccountFuturesSummaryV3
from .sub_account_margin_summary import SubAccountMarginSummary
from .sub_account_spot_summary import SubAccountSpotSummary
from .sub_account_transfer_futures import SubAccountTransferFutures
from .sub_account_transfer_history_futures import SubAccountTransferHistoryFutures
from .sub_account_transfer_history_spot import SubAccountTransferHistorySpot
from .sub_account_transfer_spot import SubAccountTransferSpot
from .sub_account_usdm_futures_commission import SubAccountUsdmFuturesCommission
from .universal_transfer import UniversalTransfer
from .universal_transfer_history import UniversalTransferHistory
from .update_sub_account_api_ip_restriction_v2 import UpdateSubAccountApiIpRestrictionV2


class Broker(
  BnbBurnStatus,
  ChangeSubAccountApiPermission,
  ChangeSubAccountCoinmFuturesCommission,
  ChangeSubAccountCommission,
  ChangeSubAccountUsdmFuturesCommission,
  CommissionRebateRecentRecordFutures,
  CommissionRebateRecentRecordSpot,
  CreateSubAccount,
  CreateSubAccountApiKey,
  DeleteSubAccountApiIpRestriction,
  DeleteSubAccountApiKey,
  EnableBnbBurnMarginInterest,
  EnableBnbBurnSpotMargin,
  EnableSubAccountFutures,
  EnableUniversalTransferPermission,
  Info,
  SubAccount,
  SubAccountApiIpRestriction,
  SubAccountApiKey,
  SubAccountCoinmFuturesCommission,
  SubAccountDepositHistory,
  SubAccountFuturesSummary,
  SubAccountFuturesSummaryV2,
  SubAccountFuturesSummaryV3,
  SubAccountMarginSummary,
  SubAccountSpotSummary,
  SubAccountTransferFutures,
  SubAccountTransferHistoryFutures,
  SubAccountTransferHistorySpot,
  SubAccountTransferSpot,
  SubAccountUsdmFuturesCommission,
  UniversalTransfer,
  UniversalTransferHistory,
  UpdateSubAccountApiIpRestrictionV2,
):
  """Binance broker endpoints."""
