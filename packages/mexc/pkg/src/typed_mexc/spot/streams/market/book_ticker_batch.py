from typing_extensions import Any
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_mexc.spot.streams.core import SpotStreamsEndpoint
from typed_mexc.spot.streams.core.proto import PublicBookTickerBatchV3Api


@dataclass(kw_only=True, frozen=True)
class BookTickerBatch(SpotStreamsEndpoint):
  def book_ticker_batch(self, symbol: str) -> StreamManager[PublicBookTickerBatchV3Api, Any, Any]:
    """Subscribe to a batch of best bid/ask updates for one spot trading pair.

    Args:
      symbol: Uppercase spot trading pair, for example `BTCUSDT`.

    References:
      - [MEXC API docs](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams/individual-symbol-book-ticker-streams-batch-aggregation)
    """
    channel = f'spot@public.bookTicker.batch.v3.api.pb@{symbol}'
    return self.subscribe(channel, meta={'proto_field': 'public_book_ticker_batch'})
