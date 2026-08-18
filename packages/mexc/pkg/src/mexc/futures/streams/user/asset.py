from dataclasses import dataclass
from decimal import Decimal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import AuthedStreamsMixin

class Asset(TypedDict, total=False):
  currency: str
  availableBalance: Decimal
  frozenBalance: Decimal
  positionMargin: Decimal
  bonus: Decimal

validate_response = validator(Asset)

@dataclass
class AssetStream(AuthedStreamsMixin):
  def asset(self, *, validate: bool = True) -> StreamManager[Asset, None, None]:
    """
    Subscribe to futures asset updates.

    Args:
      validate: Validate pushed asset payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#asset-information)
    """
    return StreamManager(lambda: self._asset_impl(validate=validate))

  async def _asset_impl(self, *, validate: bool = True) -> Stream[Asset, None, None]:
    stream = await self.authenticated_ws.subscribe('personal.asset')
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
