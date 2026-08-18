from .agg_trades import AggTrades
from .avg_price import AvgPrice
from .book_ticker import BookTickerEndpoint
from .candles import Candles
from .default_symbols import DefaultSymbols
from .depth import Depth
from .etf_info import EtfInfoEndpoint
from .exchange_info import ExchangeInfo
from .historical_trades import HistoricalTrades
from .ping import Ping
from .ticker_24hr import Ticker24hr
from .ticker_price import TickerPriceEndpoint
from .time import Time
from .trades import Trades

class Market(AggTrades, AvgPrice, BookTickerEndpoint, Candles, DefaultSymbols, Depth, EtfInfoEndpoint, ExchangeInfo, HistoricalTrades, Ping, Ticker24hr, TickerPriceEndpoint, Time, Trades):
  ...
