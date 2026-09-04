from typing_extensions import Any, Literal
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_mexc.spot.streams.core import SpotStreamsEndpoint
from typed_mexc.spot.streams.core.proto import PublicAggreDepthsV3Api


def channel_name(aggregation: Literal['100ms', '10ms'], symbol: str) -> str:
  """Build the `depth_updates` channel string for one aggregation cadence and symbol."""
  return f'spot@public.aggre.depth.v3.api.pb@{aggregation}@{symbol}'


@dataclass(kw_only=True, frozen=True)
class DepthUpdates(SpotStreamsEndpoint):
  def depth_updates(
    self, aggregation: Literal['100ms', '10ms'], symbol: str,
  ) -> StreamManager[PublicAggreDepthsV3Api, Any, Any]:
    """Subscribe to aggregated incremental order-book updates for one spot trading pair.

    Args:
      aggregation: Update aggregation cadence embedded in the channel name. MEXC
        documents `100ms` and `10ms`.
      symbol: Uppercase spot trading pair, for example `BTCUSDT`.

    References:
      - [MEXC API docs](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams/limit-depth-streams)
    """
    channel = channel_name(aggregation, symbol)
    return self.subscribe(channel, meta={'proto_field': 'public_aggre_depths'})
