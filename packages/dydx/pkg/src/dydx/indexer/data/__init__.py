"""Grouped HTTP indexer data endpoints."""

from dataclasses import dataclass

from .core import INDEXER_HTTP_URL, INDEXER_TESTNET_HTTP_URL
from .get_asset_positions import GetAssetPositions
from .get_candles import GetCandlesPaged
from .get_compliance_screen import GetComplianceScreen
from .get_fills import GetFillsPaged
from .get_funding_payments import GetFundingPaymentsPaged
from .get_funding_payments_for_parent_subaccount import (
  GetFundingPaymentsForParentSubaccountPaged,
)
from .get_height import GetHeight
from .get_historical_funding import GetHistoricalFundingPaged
from .get_historical_pnl import GetHistoricalPnl
from .get_market import GetMarket
from .get_megavault_historical_pnl import GetMegavaultHistoricalPnl
from .get_order import GetOrder
from .get_order_book import GetOrderBook
from .get_parent_asset_positions import GetParentAssetPositions
from .get_parent_fills import GetParentFills
from .get_parent_historical_pnl import GetParentHistoricalPnl
from .get_parent_subaccount import GetParentSubaccount
from .get_parent_transfers import GetParentTransfers
from .get_rewards import GetRewards
from .get_rewards_aggregated import GetRewardsAggregated
from .get_screen import GetScreen
from .get_sparklines import GetSparklines
from .get_subaccount import GetSubaccount
from .get_subaccounts import GetSubaccounts
from .get_time import GetTime
from .get_trades import GetTrades
from .get_transfers import GetTransfersPaged
from .get_transfers_between import GetTransfersBetween
from .get_vaults_historical_pnl import GetVaultsHistoricalPnl
from .list_orders import ListOrders
from .list_parent_orders import ListParentOrders
from .list_parent_positions import ListParentPositions
from .get_open_position import GetOpenPosition


@dataclass
class IndexerData(
  GetAssetPositions,
  GetCandlesPaged,
  GetComplianceScreen,
  GetFillsPaged,
  GetFundingPaymentsPaged,
  GetFundingPaymentsForParentSubaccountPaged,
  GetHeight,
  GetHistoricalFundingPaged,
  GetHistoricalPnl,
  GetMarket,
  GetMegavaultHistoricalPnl,
  GetOrder,
  GetOrderBook,
  GetParentAssetPositions,
  GetParentFills,
  GetParentHistoricalPnl,
  GetParentSubaccount,
  GetParentTransfers,
  GetRewards,
  GetRewardsAggregated,
  GetScreen,
  GetSparklines,
  GetSubaccount,
  GetSubaccounts,
  GetTime,
  GetTrades,
  GetTransfersPaged,
  GetTransfersBetween,
  GetVaultsHistoricalPnl,
  ListOrders,
  ListParentOrders,
  ListParentPositions,
  GetOpenPosition,
):
  """HTTP indexer data endpoint group."""
