from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class ServerTime(TypedDict):
  """Current server time."""

  serverTime: Timestamp
  """Current server time."""


class Time(WsRpcEndpoint):
  """Check server time"""

  async def time(self, *, validate: bool | None = None) -> ServerTime:
    """Test connectivity to the WebSocket API and get the current server time.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#check-server-time)
    """
    _Response = ServerTime
    _validator = validator[_Response](_Response)
    return await self.request('time', validator=_validator, validate=validate)
