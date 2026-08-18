"""`GET /v5/market/rpi_orderbook` — Get RPI Orderbook."""

from typing_extensions import Literal, NotRequired, TypedDict
from bybit.core import Endpoint, validator


class RpiOrderbook(TypedDict):
  """Order book snapshot separating ordinary and RPI size."""

  s: str
  """Symbol name."""
  b: list[tuple[str, str, str]]
  """Bid levels, sorted by price in descending order."""
  a: list[tuple[str, str, str]]
  """Ask levels, sorted by price in ascending order."""
  ts: int
  """Time the snapshot was generated, as a millisecond timestamp."""
  u: int
  """Update identifier, matching the websocket order book stream."""
  seq: NotRequired[int]
  """Cross sequence number; smaller values were generated earlier."""
  cts: NotRequired[int]
  """Matching engine timestamp, matching the public trade stream."""


adapter = validator[RpiOrderbook](RpiOrderbook)


class RpiOrderbookEndpoint(Endpoint):
  """`Get RPI Orderbook` — mixed into the router that owns `market.rpi_orderbook`."""

  async def rpi_orderbook(
    self,
    *,
    category: Literal['spot', 'linear', 'inverse'] | None = None,
    symbol: str,
    limit: int,
    validate: bool | None = None,
  ) -> RpiOrderbook:
    """Get an order book snapshot that separates ordinary resting size from retail price improvement (RPI) size at each level.

    Args:
      category: Product type. Defaults to `linear` when omitted.
      symbol: Symbol name in uppercase, for example `BTCUSDT`.
      limit: Number of levels per side. Range [1, 50].
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/rpi-orderbook)
    """
    params: dict = {
      'symbol': symbol,
      'limit': limit,
    }
    if category is not None:
      params['category'] = category
    r = await self.request('GET', '/v5/market/rpi_orderbook', params=params)
    return self.result(r, adapter, validate)
