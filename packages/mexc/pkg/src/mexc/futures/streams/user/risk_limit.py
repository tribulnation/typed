from dataclasses import dataclass
from decimal import Decimal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import AuthedStreamsMixin

class RiskLimit(TypedDict, total=False):
  symbol: str
  positionType: int
  riskSource: int
  level: int
  maxVol: Decimal
  maxLeverage: int
  mmr: Decimal
  imr: Decimal

validate_response = validator(RiskLimit)

@dataclass
class RiskLimitStream(AuthedStreamsMixin):
  def risk_limit(self, *, validate: bool = True) -> StreamManager[RiskLimit, None, None]:
    """
    Subscribe to futures risk-limit updates.

    Args:
      validate: Validate pushed risk-limit payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#risk-limit)
    """
    return StreamManager(lambda: self._risk_limit_impl(validate=validate))

  async def _risk_limit_impl(self, *, validate: bool = True) -> Stream[RiskLimit, None, None]:
    stream = await self.authenticated_ws.subscribe('personal.risk.limit')
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
