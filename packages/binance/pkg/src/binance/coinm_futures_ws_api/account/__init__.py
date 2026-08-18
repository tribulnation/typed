from .balance import Balance
from .position import Position
from .status import Status


class Account(Balance, Position, Status):
  """Binance account endpoints."""
