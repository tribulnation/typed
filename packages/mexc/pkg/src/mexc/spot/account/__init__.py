from .info import Info
from .kyc_status import KycStatus
from .mx_deduct_enable import MxDeductEnable
from .mx_deduct_status import MxDeductStatus
from .open_orders import OpenOrders
from .order import Order
from .orders import Orders
from .self_symbols import SelfSymbols
from .trade_fee import TradeFee
from .trades import Trades

class Account(Info, KycStatus, MxDeductEnable, MxDeductStatus, OpenOrders, Order, Orders, SelfSymbols, TradeFee, Trades):
  ...
