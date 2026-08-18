from dataclasses import dataclass
from typing_extensions import Literal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.futures.streams.core import StreamsMixin, Reply
from .depth import Depth, validate_response

DepthLimit = Literal[5, 10, 20]

@dataclass
class DepthFull(StreamsMixin):
  def depth_full(
    self, symbol: str, *, limit: DepthLimit = 20, validate: bool = True,
  ) -> StreamManager[Depth, Reply, Reply]:
    """
    Subscribe to futures full-depth snapshots.

    Args:
      symbol: Futures contract symbol, for example `BTC_USDT`.
      limit: Number of price levels in each snapshot.
      validate: Validate pushed depth payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#filter-subscription)
    """
    return StreamManager(lambda: self._depth_full_impl(symbol, limit=limit, validate=validate))

  async def _depth_full_impl(
    self, symbol: str, *, limit: DepthLimit = 20, validate: bool = True,
  ) -> Stream[Depth, Reply, Reply]:
    stream = await self.subscribe('depth.full', {'symbol': symbol, 'limit': limit})
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
