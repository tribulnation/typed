"""`GET /api/v1/level2/depth{size}` — Get Part OrderBook."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesPartOrderBook(TypedDict):
  """Order book depth for one contract, up to `size` levels per side."""

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


_Type = FuturesPartOrderBook
adapter = validator[_Type](_Type)  # type: ignore


class PartOrderbook(RpcEndpoint):
  """`Get Part OrderBook` — mixed into `Futures`, the product exposing `futures.part_orderbook`."""

  async def part_orderbook(
    self,
    size: Literal['20', '100'],
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> FuturesPartOrderBook:
    """Get order book depth for one futures contract, limited to the requested number of price levels per side. Faster and lighter than the full order book when a caller does not need every level.

    Args:
      size: Number of price levels per side to return. Confirmed live: `20` and `100` are valid; `50` returns HTTP 404.
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
      f'/api/v1/level2/depth{size}',
      params=params,
      validator=adapter,
      validate=validate,
    )
