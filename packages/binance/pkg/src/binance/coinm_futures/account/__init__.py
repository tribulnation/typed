from .account import Account as AccountAsAccount
from .balance import Balance
from .commission_rate import CommissionRate
from .income import Income
from .leverage_bracket_by_pair import LeverageBracketByPair
from .leverage_bracket_by_symbol import LeverageBracketBySymbol
from .listen_key_close import ListenKeyClose
from .listen_key_keepalive import ListenKeyKeepalive
from .listen_key_start import ListenKeyStart
from .order_history_download_id import OrderHistoryDownloadId
from .order_history_download_link import OrderHistoryDownloadLink
from .pm_account_info import PmAccountInfo
from .trade_history_download_id import TradeHistoryDownloadId
from .trade_history_download_link import TradeHistoryDownloadLink
from .transaction_history_download_id import TransactionHistoryDownloadId
from .transaction_history_download_link import TransactionHistoryDownloadLink


class Account(
  AccountAsAccount,
  Balance,
  CommissionRate,
  Income,
  LeverageBracketByPair,
  LeverageBracketBySymbol,
  ListenKeyClose,
  ListenKeyKeepalive,
  ListenKeyStart,
  OrderHistoryDownloadId,
  OrderHistoryDownloadLink,
  PmAccountInfo,
  TradeHistoryDownloadId,
  TradeHistoryDownloadLink,
  TransactionHistoryDownloadId,
  TransactionHistoryDownloadLink,
):
  """Binance account endpoints."""
