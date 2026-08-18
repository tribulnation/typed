"""Hand-written PoC for the `http` surface's public-endpoint shape.

Stands in for the full generated `v2.trading.*` namespace the codegen revamp will
produce — one representative method (`tickers`), per `spec/endpoints/v2/trading/
tickers/endpoint.json`.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing_extensions import NotRequired

from bit2me.core.endpoint import RpcEndpoint
from bit2me.core.types import Timestamp
from typed_core.validation import TypedDict, validator


class Ticker(TypedDict):
  """24h ticker for one market symbol."""

  timestamp: NotRequired[Timestamp]
  symbol: NotRequired[str]
  """Market symbol."""
  open: NotRequired[Decimal]
  """Opening price (price 24 hours ago)."""
  bid: NotRequired[Decimal]
  """Highest price a buyer will pay for order."""
  ask: NotRequired[Decimal]
  """Lowest price a seller will take for order."""
  close: NotRequired[Decimal]
  """Closing price (last trade price)."""
  high: NotRequired[Decimal]
  """Highest price in the last 24 hours."""
  low: NotRequired[Decimal]
  """Lowest price in the last 24 hours."""
  percentage: NotRequired[Decimal]
  """Percentage of current price versus opening price."""
  baseVolume: NotRequired[Decimal]
  """Volume traded in terms of the base currency."""
  quoteVolume: NotRequired[Decimal]
  """Volume traded in terms of the quote currency."""


validate_tickers = validator(list[Ticker])


@dataclass(kw_only=True, frozen=True)
class V2Trading(RpcEndpoint):
  async def tickers(
    self, *, symbol: str | None = None, validate: bool | None = None
  ) -> list[Ticker]:
    """List 24h tickers, for one market or every market Bit2Me trades.

    Args:
      symbol: Market symbol to narrow to, for example `"BTC/EUR"`. Omit for every market.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/marketdata/GET/v2/trading/tickers)
    """
    params = {'symbol': symbol} if symbol is not None else None
    return await self.request(
      'GET',
      '/v2/trading/tickers',
      params=params,
      validator=validate_tickers,
      validate=validate,
    )
