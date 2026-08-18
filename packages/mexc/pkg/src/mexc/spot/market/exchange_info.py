from typing_extensions import Literal, NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.spot.core import ErrorResponse, SpotMixin

class ExchangeFiltersItem(TypedDict):
  filterType: NotRequired[str]
  """Exchange filter type."""

class RateLimitsItem(TypedDict):
  rateLimitType: NotRequired[str]
  """Rate limit type."""
  interval: NotRequired[Literal['SECOND', 'MINUTE', 'DAY']]
  """Rate limit interval unit."""
  intervalNum: NotRequired[int]
  """Number of intervals."""
  limit: NotRequired[int]
  """Request limit for the interval."""

class SymbolFilter(TypedDict):
  filterType: NotRequired[str]
  """Filter type."""
  askMultiplierDown: NotRequired[str | float]
  """Ask-side lower percent-price multiplier."""
  bidMultiplierUp: NotRequired[str | float]
  """Bid-side upper percent-price multiplier."""

class SymbolInfo(TypedDict):
  symbol: str
  """Spot symbol."""
  status: str | int
  """Symbol status."""
  baseAsset: str
  """Base asset."""
  quoteAsset: str
  """Quote asset."""
  quotePrecision: int
  """Quote asset precision."""
  baseSizePrecision: NotRequired[str | float]
  """Minimum base-size precision or step size."""
  makerCommission: str | float
  """Maker fee rate."""
  takerCommission: str | float
  """Taker fee rate."""
  orderTypes: list[str]
  """Supported order types."""
  filters: NotRequired[list[SymbolFilter]]
  """Symbol trading filters."""
  isSpotTradingAllowed: bool
  """Whether spot trading is allowed."""
  isMarginTradingAllowed: bool
  """Whether margin trading is allowed."""
  baseAssetPrecision: int
  """Returned baseAssetPrecision field."""
  fullName: str
  """Returned fullName field."""
  permissions: list[str]
  """Returned permissions field."""
  quoteAssetPrecision: int
  """Returned quoteAssetPrecision field."""
  tradeSideType: int
  """Returned tradeSideType field."""

class ExchangeInfoResponse(TypedDict):
  timezone: str
  """Exchange timezone."""
  serverTime: Timestamp
  """Server timestamp in milliseconds."""
  rateLimits: list[RateLimitsItem]
  """Rate limit entries."""
  exchangeFilters: list[ExchangeFiltersItem]
  """Exchange-level filters."""
  symbols: list[SymbolInfo]
  """Symbol trading rules."""

Response: type[ExchangeInfoResponse | ErrorResponse] = ExchangeInfoResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class ExchangeInfo(SpotMixin):
  async def exchange_info(
    self, *,
    symbol: str | None = None, symbols: str | None = None,
    validate: bool | None = None,
  ) -> ExchangeInfoResponse:
    """Return spot exchange metadata and symbol trading rules.

    Args:
      symbol: Single spot symbol to query.
      symbols: Comma-separated spot symbols to query.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#exchange-information)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if symbols is not None:
      params['symbols'] = symbols
    r = await self.request('GET', '/api/v3/exchangeInfo', params=params)
    return self.output(r.text, adapter, validate)
