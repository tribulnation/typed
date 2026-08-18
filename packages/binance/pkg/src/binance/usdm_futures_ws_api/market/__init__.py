from .depth import Depth
from .ticker_book import TickerBook
from .ticker_price import TickerPrice


class Market(Depth, TickerBook, TickerPrice):
  """Binance market endpoints."""
