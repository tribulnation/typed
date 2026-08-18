"""KuCoin Market endpoints."""

from .all_tickers import AllTickers
from .call_auction_info import CallAuctionInfo
from .call_auction_orderbook_level50 import CallAuctionOrderbookLevel50
from .index_price import IndexPrice
from .klines import Klines
from .mark_price import MarkPrice
from .market_snapshot import MarketSnapshot
from .orderbook_increment import OrderbookIncrement
from .orderbook_level1 import OrderbookLevel1
from .orderbook_level5 import OrderbookLevel5
from .orderbook_level50 import OrderbookLevel50
from .symbol_snapshot import SymbolSnapshot
from .ticker import Ticker
from .trade import Trade


class Market(
  AllTickers,
  CallAuctionInfo,
  CallAuctionOrderbookLevel50,
  IndexPrice,
  Klines,
  MarkPrice,
  MarketSnapshot,
  OrderbookIncrement,
  OrderbookLevel1,
  OrderbookLevel5,
  OrderbookLevel50,
  SymbolSnapshot,
  Ticker,
  Trade,
):
  """KuCoin Market endpoints."""
