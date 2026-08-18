from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import StreamsMixin, Reply

class Ticker(TypedDict, total=False):
  symbol: str
  contractId: int
  lastPrice: Decimal
  bid1: Decimal
  ask1: Decimal
  volume24: Decimal
  holdVol: Decimal
  indexPrice: Decimal
  fairPrice: Decimal
  fundingRate: Decimal
  timestamp: datetime

validate_response = validator(Ticker)

@dataclass
class TickerStream(StreamsMixin):
  def ticker(self, symbol: str, *, validate: bool = True) -> StreamManager[Ticker, Reply, Reply]:
    """
    Subscribe to ticker updates for one futures contract.

    Args:
      symbol: Futures contract symbol, for example `BTC_USDT`.
      validate: Validate pushed ticker payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#filter-subscription)
    """
    return StreamManager(lambda: self._ticker_impl(symbol, validate=validate))

  async def _ticker_impl(self, symbol: str, *, validate: bool = True) -> Stream[Ticker, Reply, Reply]:
    stream = await self.subscribe('ticker', {'symbol': symbol})
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
