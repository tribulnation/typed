from .avg_price import AvgPrice
from .block_trades_historical import BlockTradesHistorical
from .depth import Depth
from .klines import Klines
from .reference_price import ReferencePriceEndpoint
from .reference_price_calculation import ReferencePriceCalculation
from .ticker_24hr import Ticker24hr
from .ticker_book import TickerBook
from .ticker_price import TickerPrice
from .ticker_trading_day import TickerTradingDay
from .ticker_window import TickerWindow
from .trades_aggregate import TradesAggregate
from .trades_historical import TradesHistorical
from .trades_recent import TradesRecent
from .ui_klines import UiKlines


class Market(
  AvgPrice,
  BlockTradesHistorical,
  Depth,
  Klines,
  ReferencePriceEndpoint,
  ReferencePriceCalculation,
  Ticker24hr,
  TickerBook,
  TickerPrice,
  TickerTradingDay,
  TickerWindow,
  TradesAggregate,
  TradesHistorical,
  TradesRecent,
  UiKlines,
):
  """Binance market endpoints."""
