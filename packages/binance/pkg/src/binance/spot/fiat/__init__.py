from .deposit import Deposit
from .order_detail import OrderDetail
from .orders import Orders
from .payments import Payments
from .withdraw import Withdraw


class Fiat(Deposit, OrderDetail, Orders, Payments, Withdraw):
  """Binance fiat endpoints."""
