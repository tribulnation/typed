from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import AuthedStreamsMixin

class PositionMode(TypedDict, total=False):
  positionMode: int

validate_response = validator(PositionMode)

@dataclass
class PositionModeStream(AuthedStreamsMixin):
  def position_mode(self, *, validate: bool = True) -> StreamManager[PositionMode, None, None]:
    """
    Subscribe to futures position-mode updates.

    Args:
      validate: Validate pushed position-mode payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#position-mode)
    """
    return StreamManager(lambda: self._position_mode_impl(validate=validate))

  async def _position_mode_impl(self, *, validate: bool = True) -> Stream[PositionMode, None, None]:
    stream = await self.authenticated_ws.subscribe('personal.position.mode')
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
