"""`GET /v5/market/time` — Get Bybit Server Time."""

from typing_extensions import TypedDict
from bybit.core import Endpoint, validator


class ServerTime(TypedDict):
  """Current Bybit server time."""

  timeSecond: str
  """Server time, in whole seconds since the Unix epoch."""
  timeNano: str
  """Server time, in nanoseconds since the Unix epoch."""


adapter = validator[ServerTime](ServerTime)


class Time(Endpoint):
  """`Get Bybit Server Time` — mixed into the router that owns `market.time`."""

  async def time(self, *, validate: bool | None = None) -> ServerTime:
    """Get the current Bybit server time. Useful for measuring clock drift against the venue.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/time)
    """
    r = await self.request('GET', '/v5/market/time')
    return self.result(r, adapter, validate)
