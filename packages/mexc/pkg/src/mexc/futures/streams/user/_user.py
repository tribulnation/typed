from dataclasses import dataclass
from .adl_level import AdlLevelStream
from .asset import AssetStream
from .login import Login
from .my_trades import MyTrades
from .order import OrderStream
from .position import PositionStream
from .position_mode import PositionModeStream
from .risk_limit import RiskLimitStream

@dataclass
class UserStreams(
  AdlLevelStream,
  AssetStream,
  Login,
  MyTrades,
  OrderStream,
  PositionStream,
  PositionModeStream,
  RiskLimitStream,
):
  ...
