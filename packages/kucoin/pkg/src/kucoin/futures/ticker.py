"""`GET /api/v1/ticker` — Get Ticker."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesTicker(TypedDict):
  """Last trade and best bid/ask for one contract."""

  sequence: int
  """Order sequence number."""
  symbol: str
  """Contract symbol."""
  side: Literal['buy', 'sell']
  """Taker side of the last trade."""
  size: int
  """Last trade size, lots."""
  tradeId: str
  """Last trade ID."""
  price: str
  """Last traded price."""
  bestBidPrice: str
  """Best (highest) bid price."""
  bestBidSize: int
  """Size at the best bid, lots."""
  bestAskPrice: str
  """Best (lowest) ask price."""
  bestAskSize: int
  """Size at the best ask, lots."""
  ts: int
  """Snapshot timestamp, Unix **nanoseconds**."""


_Type = FuturesTicker
adapter = validator[_Type](_Type)  # type: ignore


class Ticker(RpcEndpoint):
  """`Get Ticker` — mixed into `Futures`, the product exposing `futures.ticker`."""

  async def ticker(self, *, symbol: str, validate: bool | None = None) -> FuturesTicker:
    """Get the last trade and best bid/ask for one futures contract. The equivalent data is also available via WebSocket.

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
      '/api/v1/ticker',
      params=params,
      validator=adapter,
      validate=validate,
    )
