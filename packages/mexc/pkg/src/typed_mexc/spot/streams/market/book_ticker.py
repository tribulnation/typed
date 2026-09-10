from typing_extensions import Any, Literal
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_mexc.spot.streams.core import SpotStreamsEndpoint
from typed_mexc.spot.streams.core.proto import PublicAggreBookTickerV3Api


def channel_name(aggregation: Literal['100ms', '10ms'], symbol: str) -> str:
  """Build the `book_ticker` channel string for one aggregation cadence and symbol."""
  return f'spot@public.aggre.bookTicker.v3.api.pb@{aggregation}@{symbol}'


@dataclass(kw_only=True, frozen=True)
class BookTicker(SpotStreamsEndpoint):
  """Public Spot WebSocket market streams -- aggregated deals, aggregated and
  single-symbol book ticker, order book depth (incremental and limit), and klines,
  Protocol-Buffers-framed and requiring no authentication."""

  def book_ticker(
    self, aggregation: Literal['100ms', '10ms'], symbol: str,
  ) -> StreamManager[PublicAggreBookTickerV3Api, Any, Any]:
    """Subscribe to aggregated best bid/ask updates for one spot trading pair.

    Args:
      aggregation: Update aggregation cadence embedded in the channel name. MEXC
        documents `100ms` and `10ms`.
      symbol: Uppercase spot trading pair, for example `BTCUSDT`.

    References:
      - [MEXC API docs](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams/individual-symbol-book-ticker-streams)
    """
    channel = channel_name(aggregation, symbol)
    return self.subscribe(channel, meta={'proto_field': 'public_aggre_book_ticker'})
