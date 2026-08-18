from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import StreamsMixin, Reply

class FundingRate(TypedDict, total=False):
  symbol: str
  rate: Decimal
  fundingRate: Decimal
  nextSettleTime: datetime

validate_response = validator(FundingRate)

@dataclass
class FundingRateStream(StreamsMixin):
  def funding_rate(self, symbol: str, *, validate: bool = True) -> StreamManager[FundingRate, Reply, Reply]:
    """
    Subscribe to funding-rate updates for one futures contract.

    Args:
      symbol: Futures contract symbol, for example `BTC_USDT`.
      validate: Validate pushed funding-rate payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#filter-subscription)
    """
    return StreamManager(lambda: self._funding_rate_impl(symbol, validate=validate))

  async def _funding_rate_impl(self, symbol: str, *, validate: bool = True) -> Stream[FundingRate, Reply, Reply]:
    stream = await self.subscribe('funding.rate', {'symbol': symbol})
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
