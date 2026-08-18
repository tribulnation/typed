from .accept_quote import AcceptQuote
from .asset_info import AssetInfo
from .cancel_limit_order import CancelLimitOrder
from .exchange_info import ExchangeInfo
from .get_quote import GetQuote
from .order_status import OrderStatus
from .place_limit_order import PlaceLimitOrder
from .query_limit_open_orders import QueryLimitOpenOrders
from .trade_flow import TradeFlow


class Convert(
  AcceptQuote,
  AssetInfo,
  CancelLimitOrder,
  ExchangeInfo,
  GetQuote,
  OrderStatus,
  PlaceLimitOrder,
  QueryLimitOpenOrders,
  TradeFlow,
):
  """Binance convert endpoints."""
