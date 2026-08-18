"""`GET /api/v1/level2/snapshot` — Get Full OrderBook."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesFullOrderBook(TypedDict):
  """Complete order book depth for one contract."""

  sequence: int
  """Order book sequence number."""
  symbol: str
  """Contract symbol."""
  bids: list[tuple[float, int]]
  """Buy side, every level, best (highest) price first."""
  asks: list[tuple[float, int]]
  """Sell side, every level, best (lowest) price first."""
  ts: int
  """Snapshot timestamp, Unix **nanoseconds**."""


_Type = FuturesFullOrderBook
adapter = validator[_Type](_Type)  # type: ignore


class FullOrderbook(RpcEndpoint):
  """`Get Full OrderBook` — mixed into `Futures`, the product exposing `futures.full_orderbook`."""

  async def full_orderbook(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> FuturesFullOrderBook:
    """Get the complete order book depth, every price level, for one futures contract. Resource-intensive and strictly rate-limited -- the docs recommend one initial call here, then maintaining a local book from the WebSocket incremental feed.

    Args:
      symbol: Contract symbol, e.g. `XBTUSDTM`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.request(
      'GET',
      '/api/v1/level2/snapshot',
      params=params,
      validator=adapter,
      validate=validate,
    )
