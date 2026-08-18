"""KuCoin OrdersHf endpoints."""

from .add import Add
from .add_test import AddTest
from .cancel_all_by_symbol import CancelAllBySymbol
from .cancel_by_client_oid import CancelByClientOid
from .cancel_by_order_id import CancelByOrderId
from .get_by_client_oid import GetByClientOid
from .get_by_order_id import GetByOrderId
from .get_closed_orders import GetClosedOrders
from .get_open_orders import GetOpenOrders
from .get_symbols_with_open_order import GetSymbolsWithOpenOrder
from .get_trade_history import GetTradeHistory


class OrdersHf(
  Add,
  AddTest,
  CancelAllBySymbol,
  CancelByClientOid,
  CancelByOrderId,
  GetByClientOid,
  GetByOrderId,
  GetClosedOrders,
  GetOpenOrders,
  GetSymbolsWithOpenOrder,
  GetTradeHistory,
):
  """KuCoin OrdersHf endpoints."""
