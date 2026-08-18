"""`spot.market_data.time` -- public Spot market data."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class ServerTime(TypedDict):
  """The server's current time."""

  unixtime: NotRequired[int]
  """Unix timestamp."""
  rfc1123: NotRequired[str]
  """RFC 1123 time format."""


validate_time = validator(ServerTime)


class Time(RpcEndpoint):
  """`spot.market_data.time`."""

  async def time(self) -> ServerTime:
    """Get the server's time.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/market-data/get-server-time)
    """
    return await self.request('/0/public/Time', validator=validate_time)
