from .order_book import OrderBook
from .tickers import Tickers


class Trading(OrderBook, Tickers): ...
