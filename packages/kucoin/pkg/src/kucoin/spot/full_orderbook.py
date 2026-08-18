"""`GET /api/v3/market/orderbook/level2` — Get Full OrderBook."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FullOrderBook(TypedDict):
  """Complete order book depth for one trading pair."""

  time: int
  """Snapshot timestamp, Unix ms."""
  sequence: str
  """Order book sequence number."""
  bids: list[tuple[str, str]]
  """Buy side, every level, best (highest) price first."""
  asks: list[tuple[str, str]]
  """Sell side, every level, best (lowest) price first."""


_Type = FullOrderBook
adapter = validator[_Type](_Type)  # type: ignore


class FullOrderbook(RpcEndpoint):
  """`Get Full OrderBook` — mixed into `Spot`, the product exposing `spot.full_orderbook`."""

  async def full_orderbook(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> FullOrderBook:
    """Get the complete order book depth, every price level, for one trading pair. Despite living under the Market Data section, this call is authenticated (`General` permission) — confirmed live, see `notes`. The docs recommend maintaining a local book via the WebSocket incremental feed after one initial call here, rather than polling.

    Args:
      symbol: Trading pair symbol, e.g. `BTC-USDT`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.authed_request(
      'GET',
      '/api/v3/market/orderbook/level2',
      params=params,
      validator=adapter,
      validate=validate,
    )
