from .address import Address
from .address_list import AddressList
from .credit_apply import CreditApply
from .history import History


class Deposit(Address, AddressList, CreditApply, History):
  """Binance deposit endpoints."""
