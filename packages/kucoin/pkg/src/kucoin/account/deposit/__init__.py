"""KuCoin Deposit endpoints."""

from .add import Add
from .address import Address
from .history import History


class Deposit(Add, Address, History):
  """KuCoin Deposit endpoints."""
