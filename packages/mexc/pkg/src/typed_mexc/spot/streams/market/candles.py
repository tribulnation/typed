from typing_extensions import Any, Literal
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_mexc.spot.streams.core import SpotStreamsEndpoint
from typed_mexc.spot.streams.core.proto import PublicSpotKlineV3Api

Interval = Literal[
  'Min1', 'Min5', 'Min15', 'Min30', 'Min60', 'Hour4', 'Hour8', 'Day1', 'Week1', 'Month1',
]


@dataclass(kw_only=True, frozen=True)
class Candles(SpotStreamsEndpoint):
  def candles(self, symbol: str, interval: Interval) -> StreamManager[PublicSpotKlineV3Api, Any, Any]:
    """Subscribes to one spot candlestick stream for an uppercase trading pair and
    documented interval.

    Args:
      symbol: Uppercase spot trading pair, for example `BTCUSDT`.
      interval: Kline interval. MEXC documents minute, hour, day, week, and month intervals.

    References:
      - [MEXC API docs](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams/k-line-streams)
    """
    channel = f'spot@public.kline.v3.api.pb@{symbol}@{interval}'
    return self.subscribe(channel, meta={'proto_field': 'public_spot_kline'})
