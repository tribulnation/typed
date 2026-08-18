"""KuCoin OrdersHf endpoints."""

from .add import Add
from .add_sync import AddSync
from .add_test import AddTest
from .batch_add import BatchAdd
from .batch_add_sync import BatchAddSync
from .cancel_all import CancelAll
from .cancel_all_by_symbol import CancelAllBySymbol
from .cancel_by_client_oid import CancelByClientOid
from .cancel_by_client_oid_sync import CancelByClientOidSync
from .cancel_by_order_id import CancelByOrderId
from .cancel_by_order_id_sync import CancelByOrderIdSync
from .cancel_partial import CancelPartial
from .get_by_client_oid import GetByClientOid
from .get_by_order_id import GetByOrderId
from .get_closed_orders import GetClosedOrders
from .get_dcp import GetDcp
from .get_open_orders import GetOpenOrders
from .get_open_orders_by_page import GetOpenOrdersByPage
from .get_symbols_with_open_order import GetSymbolsWithOpenOrder
from .get_trade_history import GetTradeHistory
from .modify import Modify
from .set_dcp import SetDcp


class OrdersHf(
  Add,
  AddSync,
  AddTest,
  BatchAdd,
  BatchAddSync,
  CancelAll,
  CancelAllBySymbol,
  CancelByClientOid,
  CancelByClientOidSync,
  CancelByOrderId,
  CancelByOrderIdSync,
  CancelPartial,
  GetByClientOid,
  GetByOrderId,
  GetClosedOrders,
  GetDcp,
  GetOpenOrders,
  GetOpenOrdersByPage,
  GetSymbolsWithOpenOrder,
  GetTradeHistory,
  Modify,
  SetDcp,
):
  """KuCoin OrdersHf endpoints."""
