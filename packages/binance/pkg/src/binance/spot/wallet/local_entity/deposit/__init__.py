from .history import History
from .history_v2 import HistoryV2
from .provide_info import ProvideInfo
from .provide_info_v2 import ProvideInfoV2


class Deposit(History, HistoryV2, ProvideInfo, ProvideInfoV2):
  """Binance deposit endpoints."""
