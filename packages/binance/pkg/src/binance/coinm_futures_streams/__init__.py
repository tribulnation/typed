from functools import cached_property

from binance.core.endpoint.stream import StreamEndpoint
from .agg_trade import AggTrade
from .book_ticker import BookTicker
from .book_ticker_arr import BookTickerArr
from .continuous_kline import ContinuousKline
from .contract_info import ContractInfo
from .diff_depth import DiffDepth
from .force_order import ForceOrder
from .force_order_arr import ForceOrderArr
from .index_price import IndexPrice
from .index_price_kline import IndexPriceKline
from .kline import Kline
from .mark_price import MarkPrice
from .mark_price_arr import MarkPriceArr
from .mark_price_kline import MarkPriceKline
from .mini_ticker import MiniTicker
from .mini_ticker_arr import MiniTickerArr
from .partial_depth import PartialDepth
from .ticker import Ticker
from .ticker_arr import TickerArr


class CoinMFuturesStreams(StreamEndpoint):
  """Binance coinm_futures_streams endpoints."""

  @cached_property
  def agg_trade(self) -> AggTrade:
    return AggTrade(client=self.client)

  @cached_property
  def book_ticker(self) -> BookTicker:
    return BookTicker(client=self.client)

  @cached_property
  def book_ticker_arr(self) -> BookTickerArr:
    return BookTickerArr(client=self.client)

  @cached_property
  def continuous_kline(self) -> ContinuousKline:
    return ContinuousKline(client=self.client)

  @cached_property
  def contract_info(self) -> ContractInfo:
    return ContractInfo(client=self.client)

  @cached_property
  def diff_depth(self) -> DiffDepth:
    return DiffDepth(client=self.client)

  @cached_property
  def force_order(self) -> ForceOrder:
    return ForceOrder(client=self.client)

  @cached_property
  def force_order_arr(self) -> ForceOrderArr:
    return ForceOrderArr(client=self.client)

  @cached_property
  def index_price(self) -> IndexPrice:
    return IndexPrice(client=self.client)

  @cached_property
  def index_price_kline(self) -> IndexPriceKline:
    return IndexPriceKline(client=self.client)

  @cached_property
  def kline(self) -> Kline:
    return Kline(client=self.client)

  @cached_property
  def mark_price(self) -> MarkPrice:
    return MarkPrice(client=self.client)

  @cached_property
  def mark_price_arr(self) -> MarkPriceArr:
    return MarkPriceArr(client=self.client)

  @cached_property
  def mark_price_kline(self) -> MarkPriceKline:
    return MarkPriceKline(client=self.client)

  @cached_property
  def mini_ticker(self) -> MiniTicker:
    return MiniTicker(client=self.client)

  @cached_property
  def mini_ticker_arr(self) -> MiniTickerArr:
    return MiniTickerArr(client=self.client)

  @cached_property
  def partial_depth(self) -> PartialDepth:
    return PartialDepth(client=self.client)

  @cached_property
  def ticker(self) -> Ticker:
    return Ticker(client=self.client)

  @cached_property
  def ticker_arr(self) -> TickerArr:
    return TickerArr(client=self.client)
