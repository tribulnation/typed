"""`GET /api/v1/market/orderbook/level1` — Get Ticker."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class SpotTicker(TypedDict):
  """Level 1 market data for one trading pair."""

  time: int
  """Server timestamp, Unix ms."""
  sequence: str
  """Order book sequence number."""
  price: str
  """Last traded price."""
  size: str
  """Last traded size."""
  bestBid: str
  """Best (highest) bid price."""
  bestBidSize: str
  """Size at the best bid."""
  bestAsk: str
  """Best (lowest) ask price."""
  bestAskSize: str
  """Size at the best ask."""


_Type = SpotTicker
adapter = validator[_Type](_Type)  # type: ignore


class Ticker(RpcEndpoint):
  """`Get Ticker` — mixed into `Spot`, the product exposing `spot.ticker`."""

  async def ticker(self, *, symbol: str, validate: bool | None = None) -> SpotTicker:
    """Get Level 1 market data for one trading pair: best bid/ask price and size, and the last trade's price and size.

    Args:
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
      '/api/v1/market/orderbook/level1',
      params=params,
      validator=adapter,
      validate=validate,
    )
