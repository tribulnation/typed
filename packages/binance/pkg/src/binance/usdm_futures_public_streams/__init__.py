from functools import cached_property

from binance.core.endpoint.stream import StreamEndpoint
from .book_ticker import BookTicker
from .book_ticker_arr import BookTickerArr
from .diff_depth import DiffDepth
from .partial_depth import PartialDepth
from .rpi_depth import RpiDepth


class UsdMFuturesPublicStreams(StreamEndpoint):
  """Binance usdm_futures_public_streams endpoints."""

  @cached_property
  def book_ticker(self) -> BookTicker:
    return BookTicker(client=self.client)

  @cached_property
  def book_ticker_arr(self) -> BookTickerArr:
    return BookTickerArr(client=self.client)

  @cached_property
  def diff_depth(self) -> DiffDepth:
    return DiffDepth(client=self.client)

  @cached_property
  def partial_depth(self) -> PartialDepth:
    return PartialDepth(client=self.client)

  @cached_property
  def rpi_depth(self) -> RpiDepth:
    return RpiDepth(client=self.client)
