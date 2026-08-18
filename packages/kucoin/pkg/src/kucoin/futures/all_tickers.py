"""`GET /api/v1/allTickers` — Get All Tickers."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesTickerEntry(TypedDict):
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


_Type = list[FuturesTickerEntry]
adapter = validator[_Type](_Type)  # type: ignore


class AllTickers(RpcEndpoint):
  """`Get All Tickers` — mixed into `Futures`, the product exposing `futures.all_tickers`."""

  async def all_tickers(
    self, *, validate: bool | None = None
  ) -> list[FuturesTickerEntry]:
    """Get the last trade and best bid/ask for every futures contract -- the same shape as `futures.ticker`, for every symbol at once. The equivalent data is also available via WebSocket.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.request(
      'GET',
      '/api/v1/allTickers',
      validator=adapter,
      validate=validate,
    )
