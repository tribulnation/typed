from .cancel_order import CancelOrder
from .modify_order import ModifyOrder
from .new_order import NewOrder
from .query_order import QueryOrder


class Trading(CancelOrder, ModifyOrder, NewOrder, QueryOrder):
  """Binance trading endpoints."""
