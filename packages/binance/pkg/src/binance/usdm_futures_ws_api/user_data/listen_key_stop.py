from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class Responsereply(TypedDict):
  """Always empty on success."""


class ListenKeyStop(WsRpcEndpoint):
  """Close out a user data stream."""

  async def listen_key_stop(self, *, validate: bool | None = None) -> Responsereply:
    """Close out a user data stream.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-api/user-data-streams#close-user-data-stream)
    """
    _Response = Responsereply
    _validator = validator[_Response](_Response)
    return await self.request(
      'userDataStream.stop', validator=_validator, validate=validate
    )
