from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class ExchangeAsset(TypedDict):
  """One margin asset's Multi-Assets Mode configuration."""

  asset: str
  """Asset symbol, e.g. BTC."""
  marginAvailable: bool
  """Whether this asset can be used as margin in Multi-Assets Mode."""
  autoAssetExchange: str
  """Auto-exchange threshold in Multi-Assets Mode."""


class ExchangeRateLimit(TypedDict):
  """One rate-limit bucket."""

  rateLimitType: str
  """Kind of rate limit, e.g. REQUEST_WEIGHT or ORDERS."""
  interval: str
  """Interval unit the limit resets on, e.g. MINUTE."""
  intervalNum: int
  """Number of `interval` units in one window."""
  limit: int
  """Maximum count allowed within the window."""


class SymbolFilter(TypedDict):
  """One trading-rule filter. Field applicability depends on `filterType`."""

  filterType: Literal[
    'PRICE_FILTER',
    'LOT_SIZE',
    'MARKET_LOT_SIZE',
    'MAX_NUM_ORDERS',
    'MAX_NUM_ALGO_ORDERS',
    'MIN_NOTIONAL',
    'PERCENT_PRICE',
    'POSITION_RISK_CONTROL',
  ]
  """Which filter this is."""
  minPrice: NotRequired[str]
  """PRICE_FILTER: minimum price."""
  maxPrice: NotRequired[str]
  """PRICE_FILTER: maximum price."""
  tickSize: NotRequired[str]
  """PRICE_FILTER: price increment."""
  minQty: NotRequired[str]
  """LOT_SIZE/MARKET_LOT_SIZE: minimum order quantity."""
  maxQty: NotRequired[str]
  """LOT_SIZE/MARKET_LOT_SIZE: maximum order quantity."""
  stepSize: NotRequired[str]
  """LOT_SIZE/MARKET_LOT_SIZE: quantity increment."""
  limit: NotRequired[int]
  """MAX_NUM_ORDERS/MAX_NUM_ALGO_ORDERS: maximum open order count."""
  notional: NotRequired[str]
  """MIN_NOTIONAL: minimum order notional value."""
  multiplierUp: NotRequired[str]
  """PERCENT_PRICE: upper price multiplier bound."""
  multiplierDown: NotRequired[str]
  """PERCENT_PRICE: lower price multiplier bound."""
  multiplierDecimal: NotRequired[str]
  """PERCENT_PRICE: multiplier decimal precision."""


class ExchangeSymbol(TypedDict):
  """One symbol's trading rules and metadata."""

  symbol: str
  """Trading symbol, e.g. BTCUSDT."""
  pair: str
  """Underlying pair, e.g. BTCUSDT."""
  contractType: Literal[
    'PERPETUAL', 'CURRENT_QUARTER', 'NEXT_QUARTER', 'TRADIFI_PERPETUAL'
  ]
  """Contract type."""
  deliveryDate: NotRequired[int]
  """Contract delivery date, in milliseconds since epoch."""
  onboardDate: NotRequired[int]
  """Date the symbol was listed, in milliseconds since epoch."""
  status: str
  """Trading status of the symbol, e.g. TRADING."""
  maintMarginPercent: NotRequired[str]
  """Ignore -- retained for backward compatibility, not accurate."""
  requiredMarginPercent: NotRequired[str]
  """Ignore -- retained for backward compatibility, not accurate."""
  baseAsset: str
  """Base asset, e.g. BTC."""
  quoteAsset: str
  """Quote asset, e.g. USDT."""
  marginAsset: str
  """Margin asset, e.g. USDT."""
  pricePrecision: NotRequired[int]
  """Price decimal precision. Not to be used as `tickSize` -- see the PRICE_FILTER."""
  quantityPrecision: NotRequired[int]
  """Quantity decimal precision. Not to be used as `stepSize` -- see the LOT_SIZE filter."""
  baseAssetPrecision: NotRequired[int]
  """Base asset decimal precision."""
  quotePrecision: NotRequired[int]
  """Quote asset decimal precision."""
  underlyingType: NotRequired[str]
  """Underlying asset type, e.g. COIN."""
  underlyingSubType: NotRequired[list[str]]
  """Underlying asset sub-categories, e.g. ["STORAGE"]."""
  settlePlan: NotRequired[int]
  """Settlement plan identifier."""
  triggerProtect: NotRequired[str]
  """Threshold for algo order price protection."""
  liquidationFee: NotRequired[str]
  """Liquidation fee rate for this symbol."""
  marketTakeBound: NotRequired[str]
  """Maximum price deviation a MARKET order may take from the mark price."""
  filters: list[SymbolFilter]
  """Trading rule filters applied to this symbol."""
  orderTypes: list[str]
  """Order types accepted for this symbol."""
  timeInForce: list[str]
  """Time-in-force values accepted for this symbol."""


class ExchangeInfo(TypedDict):
  """Exchange trading rules, rate limits, and symbol information."""

  timezone: str
  """Timezone the exchange's timestamps are expressed in."""
  serverTime: int
  """Current server time, in milliseconds since epoch."""
  rateLimits: list[ExchangeRateLimit]
  """Account- and IP-level rate limits."""
  exchangeFilters: list[str]
  """Exchange-wide filters. Empty on USD-M Futures as of this pass."""
  assets: list[ExchangeAsset]
  """Assets usable as margin, and their Multi-Assets Mode configuration."""
  symbols: list[ExchangeSymbol]
  """Every tradable symbol and its trading rules."""


class ExchangeInfoEndpoint(RpcEndpoint):
  """Current exchange trading rules, rate limits, and symbol information."""

  async def exchange_info(self, *, validate: bool | None = None) -> ExchangeInfo:
    """Current exchange trading rules, rate limits, and symbol information.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#exchange-information)
    """
    _Response = ExchangeInfo
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/fapi/v1/exchangeInfo', validator=_validator, validate=validate
    )
