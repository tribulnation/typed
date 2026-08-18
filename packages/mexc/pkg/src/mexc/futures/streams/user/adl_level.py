from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import AuthedStreamsMixin

class AdlLevel(TypedDict, total=False):
  positionId: int
  adlLevel: int

validate_response = validator(AdlLevel)

@dataclass
class AdlLevelStream(AuthedStreamsMixin):
  def adl_level(self, *, validate: bool = True) -> StreamManager[AdlLevel, None, None]:
    """
    Subscribe to futures ADL level updates.

    Args:
      validate: Validate pushed ADL level payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#position-adl-level)
    """
    return StreamManager(lambda: self._adl_level_impl(validate=validate))

  async def _adl_level_impl(self, *, validate: bool = True) -> Stream[AdlLevel, None, None]:
    stream = await self.authenticated_ws.subscribe('personal.adl.level')
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
