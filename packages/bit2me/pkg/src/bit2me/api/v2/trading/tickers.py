from decimal import Decimal
from typing_extensions import NotRequired, TypedDict
from bit2me.types import MillisTimestamp
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Entry(TypedDict):
  timestamp: NotRequired[MillisTimestamp]
  symbol: NotRequired[str]
  """Market symbol"""
  open: NotRequired[Decimal]
  """Opening price (price 24 horus ago)"""
  bid: NotRequired[Decimal]
  """Highest price a buyer will pay for order"""
  ask: NotRequired[Decimal]
  """Lowest price a seller will take for order"""
  close: NotRequired[Decimal]
  """Closing price (last trade price)"""
  high: NotRequired[Decimal]
  """Highest price in the last 24 hours"""
  low: NotRequired[Decimal]
  """Lowest price in the last 24 hours"""
  percentage: NotRequired[Decimal]
  """Percentage of current price versus opening price"""
  baseVolume: NotRequired[Decimal]
  """Volume traded in terms of the base currency"""
  quoteVolume: NotRequired[Decimal]
  """Volume traded in terms of the quote currency"""


validate_response = validator(list[Entry])


class Tickers(RpcEndpoint):
  async def tickers(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[Entry]:
    """Get ticker information (OHLCV, current best bid and ask, percentage versus price 24 hours ago) for all markets or by requested market symbol. The data refers to the last 24 hours from the date indicated by the timestamp.

    Args:
      symbol: Market symbol (optional, default all markets)
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/marketdata/GET/v2/trading/tickers)
    """
    params = {'symbol': symbol} if symbol is not None else None
    return await self.request(
      'GET',
      '/v2/trading/tickers',
      params=params,
      validator=validate_response,
      validate=validate,
    )
