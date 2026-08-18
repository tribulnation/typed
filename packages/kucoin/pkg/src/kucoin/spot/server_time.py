"""`GET /api/v1/timestamp` — Get Server Time."""

from datetime import datetime
from typed_core.validation import validator
from kucoin.core import RpcEndpoint, timestamp

adapter = validator(int)


class ServerTime(RpcEndpoint):
  """`Get Server Time` — mixed into `Spot`, the product exposing `spot.server_time`."""

  async def server_time(self, *, validate: bool | None = None) -> datetime:
    """Get the current KuCoin Spot/Margin server time.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    ms = await self.request(
      'GET', '/api/v1/timestamp', validator=adapter, validate=validate
    )
    return timestamp.parse(ms)
