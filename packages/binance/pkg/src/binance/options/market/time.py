from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class ServerTime(TypedDict):
  """Current server time."""

  serverTime: NotRequired[Timestamp]
  """Current server time."""


class Time(RpcEndpoint):
  """Test connectivity to the Options REST API and get the current server time."""

  async def time(self, *, validate: bool | None = None) -> ServerTime:
    """Test connectivity to the Options REST API and get the current server time.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/market-data#check-server-time)
    """
    _Response = ServerTime
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/eapi/v1/time', validator=_validator, validate=validate
    )
