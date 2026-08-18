"""`GET /api/v1/market/histories` — Get Trade History."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class SpotTrade(TypedDict):
  """One executed trade."""

  sequence: str
  """Trade sequence number."""
  tradeId: str
  """Same value as `sequence`. Undocumented, observed live."""
  price: str
  """Execution price."""
  size: str
  """Quantity traded, base currency."""
  side: Literal['buy', 'sell']
  """Taker side of the trade."""
  time: int
  """Trade time, Unix **nanoseconds** (not milliseconds)."""


_Type = list[SpotTrade]
adapter = validator[_Type](_Type)  # type: ignore


class TradeHistory(RpcEndpoint):
  """`Get Trade History` — mixed into `Spot`, the product exposing `spot.trade_history`."""

  async def trade_history(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> list[SpotTrade]:
    """Get the most recent trades for one trading pair, up to the last 100. No time-range parameters — this endpoint always returns the tail of the trade stream, not a paginated history.

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
      '/api/v1/market/histories',
      params=params,
      validator=adapter,
      validate=validate,
    )
