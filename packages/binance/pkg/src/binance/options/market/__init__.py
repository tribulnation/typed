from .block_trades import BlockTrades
from .depth import Depth
from .exchange_info import ExchangeInfoEndpoint
from .exercise_history import ExerciseHistory
from .index import Index
from .klines import Klines
from .mark import Mark
from .open_interest import OpenInterestEndpoint
from .ping import Ping
from .ticker import Ticker
from .time import Time
from .trades import Trades


class Market(
  BlockTrades,
  Depth,
  ExchangeInfoEndpoint,
  ExerciseHistory,
  Index,
  Klines,
  Mark,
  OpenInterestEndpoint,
  Ping,
  Ticker,
  Time,
  Trades,
):
  """Binance market endpoints."""
