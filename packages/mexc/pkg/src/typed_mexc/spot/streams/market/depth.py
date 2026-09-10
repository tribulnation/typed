from typing_extensions import Any, Literal
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_mexc.spot.streams.core import SpotStreamsEndpoint
from typed_mexc.spot.streams.core.proto import PublicLimitDepthsV3Api


@dataclass(kw_only=True, frozen=True)
class Depth(SpotStreamsEndpoint):
  def depth(
    self, symbol: str, level: Literal[5, 10, 20],
  ) -> StreamManager[PublicLimitDepthsV3Api, Any, Any]:
    """Subscribe to a fixed-depth order book snapshot stream.

    Args:
      symbol: Uppercase spot trading pair, for example `BTCUSDT`.
      level: Number of order-book levels per side pushed by the stream.

    References:
      - [MEXC API docs](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams/limit-depth-streams)
    """
    channel = f'spot@public.limit.depth.v3.api.pb@{symbol}@{level}'
    return self.subscribe(channel, meta={'proto_field': 'public_limit_depths'})
