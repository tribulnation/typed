from .change_leverage import ChangeLeverage
from .change_margin import ChangeMargin
from .change_position_mode import ChangePositionMode
from .change_risk_level import ChangeRiskLevel
from .history import History
from .leverage import Leverage
from .open import Open
from .position_mode import PositionMode
from .risk_limit import RiskLimit

class Position(ChangeLeverage, ChangeMargin, ChangePositionMode, ChangeRiskLevel, History, Leverage, Open, PositionMode, RiskLimit):
  ...
