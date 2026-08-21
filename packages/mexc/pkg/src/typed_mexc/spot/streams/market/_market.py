from dataclasses import dataclass
from .book_ticker import BookTicker
from .book_ticker_batch import BookTickerBatch
from .candles import Candles
from .depth import Depth
from .depth_updates import DepthUpdates
from .trades import Trades

@dataclass
class MarketStreams(
  BookTicker,
  BookTickerBatch,
  Candles,
  Depth,
  DepthUpdates,
  Trades,
):
  ...
