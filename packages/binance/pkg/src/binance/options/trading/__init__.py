from .all_open_orders_by_underlying_cancel import AllOpenOrdersByUnderlyingCancel
from .all_open_orders_cancel import AllOpenOrdersCancel
from .batch_orders_cancel import BatchOrdersCancel
from .batch_orders_place import BatchOrdersPlace
from .commission import Commission
from .exercise_record import ExerciseRecord
from .history_orders import HistoryOrders
from .open_orders import OpenOrders
from .order_cancel import OrderCancel
from .order_new import OrderNew
from .order_query import OrderQuery
from .position import PositionEndpoint
from .stock_contract import StockContract
from .user_trades import UserTrades


class Trading(
  AllOpenOrdersByUnderlyingCancel,
  AllOpenOrdersCancel,
  BatchOrdersCancel,
  BatchOrdersPlace,
  Commission,
  ExerciseRecord,
  HistoryOrders,
  OpenOrders,
  OrderCancel,
  OrderNew,
  OrderQuery,
  PositionEndpoint,
  StockContract,
  UserTrades,
):
  """Binance trading endpoints."""
