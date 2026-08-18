from dataclasses import dataclass
from decimal import Decimal
from typing_extensions import Any

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import StreamsMixin, Reply

DepthLevel = tuple[Decimal, Decimal, int]

class Depth(TypedDict, total=False):
  asks: list[DepthLevel]
  bids: list[DepthLevel]
  version: int

validate_response = validator(Depth)

@dataclass
class DepthStream(StreamsMixin):
  def depth(
    self, symbol: str, *, compress: bool | None = None, validate: bool = True,
  ) -> StreamManager[Depth, Reply, Reply]:
    """
    Subscribe to incremental futures order-book updates.

    Args:
      symbol: Futures contract symbol, for example `BTC_USDT`.
      compress: Request merged depth updates when provided.
      validate: Validate pushed depth payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#filter-subscription)
    """
    return StreamManager(lambda: self._depth_impl(symbol, compress=compress, validate=validate))

  async def _depth_impl(
    self, symbol: str, *, compress: bool | None = None, validate: bool = True,
  ) -> Stream[Depth, Reply, Reply]:
    params: dict[str, Any] = {'symbol': symbol}
    if compress is not None:
      params['compress'] = compress
    stream = await self.subscribe('depth', params)
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
