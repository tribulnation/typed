"""`GET /api/v1/timestamp` — Get Server Time (Futures)."""

from datetime import datetime
from typed_core.validation import validator
from typed_kucoin.core import RpcEndpoint, timestamp_millis

adapter = validator(int)


class ServerTime(RpcEndpoint):
  """`Get Server Time` — mixed into `Futures`, the product exposing
  `futures.server_time`."""

  async def server_time(self, *, validate: bool | None = None) -> datetime:
    """Get the current KuCoin Futures server time.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    ms = await self.request(
      'GET', '/api/v1/timestamp', validator=adapter, validate=validate
    )
    return timestamp_millis.parse(ms)
