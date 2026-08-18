"""`GET /v5/market/orderbook` — Get Orderbook."""

from typing_extensions import Literal, NotRequired, TypedDict
from bybit.types import OrderbookLevel
from bybit.core import Endpoint, validator


class Orderbook(TypedDict):
  """Order book snapshot for one symbol."""

  s: str
  """Symbol name."""
  b: list[OrderbookLevel]
  """Bid levels, sorted by price in descending order."""
  a: list[OrderbookLevel]
  """Ask levels, sorted by price in ascending order."""
  ts: int
  """Time the snapshot was generated, as a millisecond timestamp."""
  u: int
  """Update identifier, matching the websocket order book stream."""
  seq: NotRequired[int]
  """Cross sequence number; smaller values were generated earlier."""
  cts: NotRequired[int]
  """Matching engine timestamp, matching the public trade stream."""


adapter = validator[Orderbook](Orderbook)


class OrderbookEndpoint(Endpoint):
  """`Get Orderbook` — mixed into the router that owns `market.orderbook`."""

  async def orderbook(
    self,
    *,
    category: Literal['spot', 'linear', 'inverse', 'option'],
    symbol: str,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> Orderbook:
    """Get an order book snapshot for one symbol, truncated to `limit` levels per side.

    Args:
      category: Product type.
      symbol: Symbol name in uppercase, for example `BTCUSDT`.
      limit: Number of levels per side. Range [1, 1000] for spot, linear and inverse, [1, 25] for option. Defaults vary per category.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/orderbook)
    """
    params: dict = {
      'category': category,
      'symbol': symbol,
    }
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', '/v5/market/orderbook', params=params)
    return self.result(r, adapter, validate)
