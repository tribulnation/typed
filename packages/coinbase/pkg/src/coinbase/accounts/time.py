from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class ServerTime(TypedDict):
  """The v2 API server's current time."""

  iso: str
  """Server time, ISO 8601."""
  epoch: int
  """Server time, Unix epoch seconds."""


class ServerTimeResponse(TypedDict):
  """The whole v2 wire frame — not unwrapped by the core."""

  data: ServerTime


@dataclass(frozen=True, kw_only=True)
class Time(RpcEndpoint):
  """`GET /v2/time`."""

  async def __call__(self) -> ServerTimeResponse:
    """Get the v2 API server time. No authentication required.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/track-apis/time)
    """
    return await self.request(
      'GET', '/v2/time', validator=validator(ServerTimeResponse)
    )
