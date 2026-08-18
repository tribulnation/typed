from .batch_orders import BatchOrders
from .cancel_open_orders import CancelOpenOrders
from .cancel_order import CancelOrder
from .place_order import PlaceOrder
from .test_order import TestOrder

class Trade(BatchOrders, CancelOpenOrders, CancelOrder, PlaceOrder, TestOrder):
  ...
