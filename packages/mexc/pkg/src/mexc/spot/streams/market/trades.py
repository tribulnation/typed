from dataclasses import dataclass
from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.spot.streams.core import Reply, StreamsMixin
from mexc.spot.streams.core.proto import PublicAggreDealsV3Api
from typing_extensions import Literal

def channel_name(aggregation: Literal['100ms', '10ms'], symbol: str):
  return f'spot@public.aggre.deals.v3.api.pb@{aggregation}@{symbol}'

@dataclass
class Trades(StreamsMixin):
  def trades(
    self, aggregation: Literal['100ms', '10ms'], symbol: str,
  ) -> StreamManager[PublicAggreDealsV3Api, Reply, Reply]:
    """Subscribes to raw spot trade updates for one uppercase trading pair with a 100ms or 10ms aggregation cadence. Messages are protobuf-encoded PushDataV3ApiWrapper payloads whose publicAggreDeals body contains the decoded trades.

    Args:
      aggregation: Update aggregation cadence embedded in the channel name. MEXC documents `100ms` and `10ms`.
      symbol: Uppercase spot trading pair, for example `BTCUSDT`.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#trade-streams)
    """
    return StreamManager(lambda: self._trades_impl(aggregation, symbol))

  async def _trades_impl(
    self, aggregation: Literal['100ms', '10ms'], symbol: str,
  ) -> Stream[PublicAggreDealsV3Api, Reply, Reply]:
    stream = await self.subscribe(channel_name(aggregation, symbol))
    async def parsed_stream():
      async for proto in stream:
        if proto.public_aggre_deals is not None:
          yield proto.public_aggre_deals
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
