"""`account` endpoints."""

from .account_transfer import AccountTransfer
from .add_export import AddExport
from .api_key_info import ApiKeyInfoEndpoint
from .balance import Balance
from .balance_ex import BalanceEx
from .closed_orders import ClosedOrdersEndpoint
from .create_subaccount import CreateSubaccount
from .credit_lines import CreditLines
from .export_status import ExportStatus
from .ledgers import Ledgers
from .open_orders import OpenOrdersEndpoint
from .open_positions import OpenPositions
from .order_amends import OrderAmendsEndpoint
from .query_ledgers import QueryLedgers
from .query_orders import QueryOrders
from .query_trades import QueryTrades
from .remove_export import RemoveExport
from .retrieve_export import RetrieveExport
from .trade_balance import TradeBalanceEndpoint
from .trade_volume import TradeVolumeEndpoint
from .trades_history import TradesHistory


class Account(
  AccountTransfer,
  AddExport,
  ApiKeyInfoEndpoint,
  Balance,
  BalanceEx,
  ClosedOrdersEndpoint,
  CreateSubaccount,
  CreditLines,
  ExportStatus,
  Ledgers,
  OpenOrdersEndpoint,
  OpenPositions,
  OrderAmendsEndpoint,
  QueryLedgers,
  QueryOrders,
  QueryTrades,
  RemoveExport,
  RetrieveExport,
  TradeBalanceEndpoint,
  TradeVolumeEndpoint,
  TradesHistory,
):
  """`account` endpoints."""
