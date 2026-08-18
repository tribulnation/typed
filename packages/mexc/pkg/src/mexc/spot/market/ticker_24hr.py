from typing_extensions import NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.spot.core import ErrorResponse, SpotMixin

class Ticker24hrStats(TypedDict):
  """24-hour ticker statistics."""
  symbol: str
  """Spot symbol."""
  priceChange: str
  """Absolute price change."""
  priceChangePercent: str
  """Relative price change."""
  prevClosePrice: str
  """Previous close price."""
  lastPrice: str
  """Latest traded price."""
  bidPrice: str
  """Best bid price."""
  bidQty: str
  """Best bid quantity."""
  askPrice: str
  """Best ask price."""
  askQty: str
  """Best ask quantity."""
  openPrice: str
  """Window open price."""
  highPrice: str
  """Window high price."""
  lowPrice: str
  """Window low price."""
  volume: str
  """Base asset volume."""
  quoteVolume: str
  """Quote asset volume."""
  openTime: Timestamp
  """Window open time in milliseconds."""
  closeTime: Timestamp
  """Window close time in milliseconds."""
  count: NotRequired[int | None]
  """Trade count when returned."""

class Ticker24hrStatsListItem(TypedDict):
  """24-hour ticker statistics."""
  symbol: NotRequired[str]
  """Spot symbol."""
  priceChange: NotRequired[str]
  """Absolute price change."""
  priceChangePercent: NotRequired[str]
  """Relative price change."""
  prevClosePrice: NotRequired[str]
  """Previous close price."""
  lastPrice: NotRequired[str]
  """Latest traded price."""
  bidPrice: NotRequired[str]
  """Best bid price."""
  bidQty: NotRequired[str]
  """Best bid quantity."""
  askPrice: NotRequired[str]
  """Best ask price."""
  askQty: NotRequired[str]
  """Best ask quantity."""
  openPrice: NotRequired[str]
  """Window open price."""
  highPrice: NotRequired[str]
  """Window high price."""
  lowPrice: NotRequired[str]
  """Window low price."""
  volume: NotRequired[str]
  """Base asset volume."""
  quoteVolume: NotRequired[str]
  """Quote asset volume."""
  openTime: NotRequired[Timestamp]
  """Window open time in milliseconds."""
  closeTime: NotRequired[Timestamp]
  """Window close time in milliseconds."""
  count: NotRequired[int | None]
  """Trade count when returned."""

Response: type[Ticker24hrStats | list[Ticker24hrStatsListItem] | ErrorResponse] = Ticker24hrStats | list[Ticker24hrStatsListItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class Ticker24hr(SpotMixin):
  async def ticker_24hr(
    self, *,
    symbol: str | None = None, validate: bool | None = None,
  ) -> Ticker24hrStats | list[Ticker24hrStatsListItem]:
    """Return 24-hour ticker statistics for one spot symbol or all symbols.

    Args:
      symbol: Spot symbol. If omitted, returns all symbols.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#24hr-ticker-price-change-statistics)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    r = await self.request('GET', '/api/v3/ticker/24hr', params=params)
    return self.output(r.text, adapter, validate)
