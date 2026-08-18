from .balance import Balance
from .balance_v2 import BalanceV2
from .position import Position
from .position_v2 import PositionV2
from .status import Status
from .status_v2 import StatusV2


class Account(Balance, BalanceV2, Position, PositionV2, Status, StatusV2):
  """Binance account endpoints."""
