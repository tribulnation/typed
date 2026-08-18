from .chart import Chart
from .market_data import MarketData
from .ticker import Ticker


class Currency(Chart, MarketData, Ticker): ...
