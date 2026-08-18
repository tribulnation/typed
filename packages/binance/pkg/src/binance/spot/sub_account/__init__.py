from functools import cached_property

from binance.core.endpoint.rpc import RpcEndpoint
from .add_ip_restriction import AddIpRestriction
from .api_keys import ApiKeys
from .assets import Assets
from .assets_v4 import AssetsV4
from .create_api_key import CreateApiKey
from .create_virtual import CreateVirtual
from .delete_api_key import DeleteApiKey
from .delete_ip_list import DeleteIpList
from .deposit_address import DepositAddress
from .deposit_history import DepositHistory
from .enable_futures import EnableFutures
from .enable_options import EnableOptions
from .futures_account import FuturesAccount
from .futures_account_summary import FuturesAccountSummary
from .futures_account_summary_v2 import FuturesAccountSummaryV2
from .futures_account_v2 import FuturesAccountV2
from .futures_internal_transfer import FuturesInternalTransfer
from .futures_internal_transfer_history import FuturesInternalTransferHistory
from .futures_move_position_history import FuturesMovePositionHistory
from .futures_position_risk import FuturesPositionRisk
from .futures_position_risk_v2 import FuturesPositionRiskV2
from .futures_transfer import FuturesTransfer
from .ip_restriction import IpRestriction
from .list import List
from .managed import Managed
from .margin_account import MarginAccount
from .margin_account_summary import MarginAccountSummary
from .margin_transfer import MarginTransfer
from .modify_api_key_permission import ModifyApiKeyPermission
from .move_futures_position import MoveFuturesPosition
from .own_transfer_history import OwnTransferHistory
from .spot_summary import SpotSummary
from .spot_transfer_history import SpotTransferHistory
from .status import Status
from .transaction_statistics import TransactionStatistics
from .transfer_to_master import TransferToMaster
from .transfer_to_sub import TransferToSub
from .universal_transfer import UniversalTransfer
from .universal_transfer_history import UniversalTransferHistoryEndpoint


class SubAccount(RpcEndpoint):
  """Binance sub_account endpoints."""

  @cached_property
  def add_ip_restriction(self) -> AddIpRestriction:
    return AddIpRestriction(client=self.client)

  @cached_property
  def api_keys(self) -> ApiKeys:
    return ApiKeys(client=self.client)

  @cached_property
  def assets(self) -> Assets:
    return Assets(client=self.client)

  @cached_property
  def assets_v4(self) -> AssetsV4:
    return AssetsV4(client=self.client)

  @cached_property
  def create_api_key(self) -> CreateApiKey:
    return CreateApiKey(client=self.client)

  @cached_property
  def create_virtual(self) -> CreateVirtual:
    return CreateVirtual(client=self.client)

  @cached_property
  def delete_api_key(self) -> DeleteApiKey:
    return DeleteApiKey(client=self.client)

  @cached_property
  def delete_ip_list(self) -> DeleteIpList:
    return DeleteIpList(client=self.client)

  @cached_property
  def deposit_address(self) -> DepositAddress:
    return DepositAddress(client=self.client)

  @cached_property
  def deposit_history(self) -> DepositHistory:
    return DepositHistory(client=self.client)

  @cached_property
  def enable_futures(self) -> EnableFutures:
    return EnableFutures(client=self.client)

  @cached_property
  def enable_options(self) -> EnableOptions:
    return EnableOptions(client=self.client)

  @cached_property
  def futures_account(self) -> FuturesAccount:
    return FuturesAccount(client=self.client)

  @cached_property
  def futures_account_summary(self) -> FuturesAccountSummary:
    return FuturesAccountSummary(client=self.client)

  @cached_property
  def futures_account_summary_v2(self) -> FuturesAccountSummaryV2:
    return FuturesAccountSummaryV2(client=self.client)

  @cached_property
  def futures_account_v2(self) -> FuturesAccountV2:
    return FuturesAccountV2(client=self.client)

  @cached_property
  def futures_internal_transfer(self) -> FuturesInternalTransfer:
    return FuturesInternalTransfer(client=self.client)

  @cached_property
  def futures_internal_transfer_history(self) -> FuturesInternalTransferHistory:
    return FuturesInternalTransferHistory(client=self.client)

  @cached_property
  def futures_move_position_history(self) -> FuturesMovePositionHistory:
    return FuturesMovePositionHistory(client=self.client)

  @cached_property
  def futures_position_risk(self) -> FuturesPositionRisk:
    return FuturesPositionRisk(client=self.client)

  @cached_property
  def futures_position_risk_v2(self) -> FuturesPositionRiskV2:
    return FuturesPositionRiskV2(client=self.client)

  @cached_property
  def futures_transfer(self) -> FuturesTransfer:
    return FuturesTransfer(client=self.client)

  @cached_property
  def ip_restriction(self) -> IpRestriction:
    return IpRestriction(client=self.client)

  @cached_property
  def list(self) -> List:
    return List(client=self.client)

  @cached_property
  def managed(self) -> Managed:
    return Managed(client=self.client)

  @cached_property
  def margin_account(self) -> MarginAccount:
    return MarginAccount(client=self.client)

  @cached_property
  def margin_account_summary(self) -> MarginAccountSummary:
    return MarginAccountSummary(client=self.client)

  @cached_property
  def margin_transfer(self) -> MarginTransfer:
    return MarginTransfer(client=self.client)

  @cached_property
  def modify_api_key_permission(self) -> ModifyApiKeyPermission:
    return ModifyApiKeyPermission(client=self.client)

  @cached_property
  def move_futures_position(self) -> MoveFuturesPosition:
    return MoveFuturesPosition(client=self.client)

  @cached_property
  def own_transfer_history(self) -> OwnTransferHistory:
    return OwnTransferHistory(client=self.client)

  @cached_property
  def spot_summary(self) -> SpotSummary:
    return SpotSummary(client=self.client)

  @cached_property
  def spot_transfer_history(self) -> SpotTransferHistory:
    return SpotTransferHistory(client=self.client)

  @cached_property
  def status(self) -> Status:
    return Status(client=self.client)

  @cached_property
  def transaction_statistics(self) -> TransactionStatistics:
    return TransactionStatistics(client=self.client)

  @cached_property
  def transfer_to_master(self) -> TransferToMaster:
    return TransferToMaster(client=self.client)

  @cached_property
  def transfer_to_sub(self) -> TransferToSub:
    return TransferToSub(client=self.client)

  @cached_property
  def universal_transfer(self) -> UniversalTransfer:
    return UniversalTransfer(client=self.client)

  @cached_property
  def universal_transfer_history(self) -> UniversalTransferHistoryEndpoint:
    return UniversalTransferHistoryEndpoint(client=self.client)
