from functools import cached_property

from binance.core.endpoint.stream import StreamEndpoint
from .book_ticker import BookTicker
from .depth import Depth
from .diff_depth import DiffDepth
from .index_arr import IndexArr
from .kline import KlineEndpoint
from .mark_price import MarkPrice
from .open_interest import OpenInterest
from .option_symbol import OptionSymbol
from .ticker import Ticker
from .ticker_by_expiration import TickerByExpiration
from .trade import Trade


class OptionsStreams(StreamEndpoint):
  """Binance options_streams endpoints."""

  @cached_property
  def book_ticker(self) -> BookTicker:
    return BookTicker(client=self.client)

  @cached_property
  def depth(self) -> Depth:
    return Depth(client=self.client)

  @cached_property
  def diff_depth(self) -> DiffDepth:
    return DiffDepth(client=self.client)

  @cached_property
  def index_arr(self) -> IndexArr:
    return IndexArr(client=self.client)

  @cached_property
  def kline(self) -> KlineEndpoint:
    return KlineEndpoint(client=self.client)

  @cached_property
  def mark_price(self) -> MarkPrice:
    return MarkPrice(client=self.client)

  @cached_property
  def open_interest(self) -> OpenInterest:
    return OpenInterest(client=self.client)

  @cached_property
  def option_symbol(self) -> OptionSymbol:
    return OptionSymbol(client=self.client)

  @cached_property
  def ticker(self) -> Ticker:
    return Ticker(client=self.client)

  @cached_property
  def ticker_by_expiration(self) -> TickerByExpiration:
    return TickerByExpiration(client=self.client)

  @cached_property
  def trade(self) -> Trade:
    return Trade(client=self.client)
