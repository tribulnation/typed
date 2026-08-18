"""KuCoin Private endpoints."""

from .all_orders import AllOrders
from .all_positions import AllPositions
from .balance import Balance
from .cross_leverage import CrossLeverage
from .margin_mode import MarginMode
from .order import Order
from .position import Position
from .stop_order import StopOrder


class Private(
  AllOrders,
  AllPositions,
  Balance,
  CrossLeverage,
  MarginMode,
  Order,
  Position,
  StopOrder,
):
  """KuCoin Private endpoints."""
