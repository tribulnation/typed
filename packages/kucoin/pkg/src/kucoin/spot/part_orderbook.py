"""`GET /api/v1/market/orderbook/level2_{size}` — Get Part OrderBook."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class PartOrderBook(TypedDict):
  """Order book depth aggregated by price, up to `size` levels per side."""

  time: int
  """Snapshot timestamp, Unix ms."""
  sequence: str
  """Order book sequence number."""
  bids: list[tuple[str, str]]
  """Buy side, best (highest) price first."""
  asks: list[tuple[str, str]]
  """Sell side, best (lowest) price first."""


_Type = PartOrderBook
adapter = validator[_Type](_Type)  # type: ignore


class PartOrderbook(RpcEndpoint):
  """`Get Part OrderBook` — mixed into `Spot`, the product exposing `spot.part_orderbook`."""

  async def part_orderbook(
    self,
    size: Literal['20', '100'],
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> PartOrderBook:
    """Get order book depth aggregated by price, limited to the requested number of price levels per side. Recommended over Full OrderBook when the caller doesn't need every level — faster and lighter.

    Args:
      size: Number of price levels per side to return.
      symbol: Trading pair symbol, e.g. `BTC-USDT`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.request(
      'GET',
      f'/api/v1/market/orderbook/level2_{size}',
      params=params,
      validator=adapter,
      validate=validate,
    )
