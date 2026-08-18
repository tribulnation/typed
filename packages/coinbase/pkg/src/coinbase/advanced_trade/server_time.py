from dataclasses import dataclass
from datetime import datetime
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class ServerTime(TypedDict):
  """The current Advanced Trade server time, in three representations."""

  iso: datetime
  """ISO-8601 representation of the current time."""
  epochSeconds: str
  """Second-precision UNIX timestamp."""
  epochMillis: str
  """Millisecond-precision UNIX timestamp."""


@dataclass(frozen=True, kw_only=True)
class ServerTimeEndpoint(RpcEndpoint):
  """`GET /api/v3/brokerage/time`."""

  async def __call__(self) -> ServerTime:
    """Get the current Advanced Trade server time. No authentication required — verified live (both a signed and unsigned call succeed identically).

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/public/get-server-time)
    """
    return await self.request(
      'GET', '/api/v3/brokerage/time', validator=validator(ServerTime)
    )
