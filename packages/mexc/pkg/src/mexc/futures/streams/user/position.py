from dataclasses import dataclass
from decimal import Decimal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import AuthedStreamsMixin

class Position(TypedDict, total=False):
  positionId: int
  symbol: str
  positionType: int
  openType: int
  state: int
  holdVol: Decimal
  frozenVol: Decimal
  closeVol: Decimal
  holdAvgPrice: Decimal
  openAvgPrice: Decimal
  closeAvgPrice: Decimal
  liquidatePrice: Decimal
  leverage: int
  realised: Decimal
  autoAddIm: bool

validate_response = validator(Position)

@dataclass
class PositionStream(AuthedStreamsMixin):
  def position(self, *, validate: bool = True) -> StreamManager[Position, None, None]:
    """
    Subscribe to futures position updates.

    Args:
      validate: Validate pushed position payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#position-information)
    """
    return StreamManager(lambda: self._position_impl(validate=validate))

  async def _position_impl(self, *, validate: bool = True) -> Stream[Position, None, None]:
    stream = await self.authenticated_ws.subscribe('personal.position')
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
