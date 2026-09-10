from typing_extensions import Any, Literal
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_mexc.spot.streams.core import SpotStreamsEndpoint
from typed_mexc.spot.streams.core.proto import PublicAggreDealsV3Api


def channel_name(aggregation: Literal['100ms', '10ms'], symbol: str) -> str:
  """Build the `trades` channel string for one aggregation cadence and symbol."""
  return f'spot@public.aggre.deals.v3.api.pb@{aggregation}@{symbol}'


@dataclass(kw_only=True, frozen=True)
class Trades(SpotStreamsEndpoint):
  def trades(
    self, aggregation: Literal['100ms', '10ms'], symbol: str,
  ) -> StreamManager[PublicAggreDealsV3Api, Any, Any]:
    """Subscribe to aggregated trade updates for one spot trading pair.

    Args:
      aggregation: Update aggregation cadence embedded in the channel name. MEXC
        documents `100ms` and `10ms`.
      symbol: Uppercase spot trading pair, for example `BTCUSDT`.

    References:
      - [MEXC API docs](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams/trade-streams)
    """
    channel = channel_name(aggregation, symbol)
    return self.subscribe(channel, meta={'proto_field': 'public_aggre_deals'})
