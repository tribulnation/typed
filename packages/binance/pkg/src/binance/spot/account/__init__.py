from .all_order_lists import AllOrderLists
from .all_orders import AllOrders
from .commission import Commission
from .info import Info
from .my_allocations import MyAllocations
from .my_filters import MyFilters
from .my_prevented_matches import MyPreventedMatches
from .my_trades import MyTrades
from .open_order_lists import OpenOrderLists
from .open_orders import OpenOrders
from .order import Order
from .order_amendments import OrderAmendments
from .order_list import OrderList
from .rate_limit_order import RateLimitOrder


class Account(
  AllOrderLists,
  AllOrders,
  Commission,
  Info,
  MyAllocations,
  MyFilters,
  MyPreventedMatches,
  MyTrades,
  OpenOrderLists,
  OpenOrders,
  Order,
  OrderAmendments,
  OrderList,
  RateLimitOrder,
):
  """Binance account endpoints."""
