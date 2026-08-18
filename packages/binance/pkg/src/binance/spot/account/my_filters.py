from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class ExchangeMaxNumAlgoOrdersFilter(TypedDict):
  """Maximum number of "algo" orders (STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT) this account may have open on the exchange."""

  filterType: Literal['EXCHANGE_MAX_NUM_ALGO_ORDERS']
  """Filter type discriminator."""
  maxNumAlgoOrders: int
  """Maximum number of open algo orders allowed on the exchange."""


class ExchangeMaxNumIcebergOrdersFilter(TypedDict):
  """Maximum number of iceberg orders this account may have open on the exchange."""

  filterType: Literal['EXCHANGE_MAX_NUM_ICEBERG_ORDERS']
  """Filter type discriminator."""
  maxNumIcebergOrders: int
  """Maximum number of open iceberg orders allowed on the exchange."""


class ExchangeMaxNumOrderListsFilter(TypedDict):
  """Maximum number of order lists this account may have open on the exchange (OTOCOs count as one order list)."""

  filterType: Literal['EXCHANGE_MAX_NUM_ORDER_LISTS']
  """Filter type discriminator."""
  maxNumOrderLists: int
  """Maximum number of open order lists allowed on the exchange."""


class ExchangeMaxNumOrdersFilter(TypedDict):
  """Maximum number of orders this account may have open on the exchange (algo and normal orders both count)."""

  filterType: Literal['EXCHANGE_MAX_NUM_ORDERS']
  """Filter type discriminator."""
  maxNumOrders: int
  """Maximum number of open orders allowed on the exchange."""


class IcebergPartsFilter(TypedDict):
  """Maximum parts an iceberg order can have on the symbol, computed as CEIL(qty / icebergQty)."""

  filterType: Literal['ICEBERG_PARTS']
  """Filter type discriminator."""
  limit: int
  """Maximum number of iceberg parts allowed."""


class LotSizeFilter(TypedDict):
  """Quantity rules for the symbol."""

  filterType: Literal['LOT_SIZE']
  """Filter type discriminator."""
  minQty: str
  """Minimum quantity/icebergQty allowed, as a decimal string."""
  maxQty: str
  """Maximum quantity/icebergQty allowed, as a decimal string."""
  stepSize: str
  """Interval that quantity/icebergQty can be increased or decreased by, as a decimal string."""


class MarketLotSizeFilter(TypedDict):
  """Quantity rules for MARKET orders on the symbol."""

  filterType: Literal['MARKET_LOT_SIZE']
  """Filter type discriminator."""
  minQty: str
  """Minimum MARKET order quantity allowed, as a decimal string."""
  maxQty: str
  """Maximum MARKET order quantity allowed, as a decimal string."""
  stepSize: str
  """Interval that a MARKET order quantity can be increased or decreased by, as a decimal string."""


class MaxAssetFilter(TypedDict):
  """Maximum quantity of an asset this account is allowed to transact in a single order. Applies to order quantity when the asset is the symbol's base asset, or to notional value when it is the quote asset."""

  filterType: Literal['MAX_ASSET']
  """Filter type discriminator."""
  asset: str
  """Asset this filter applies to."""
  limit: str
  """Maximum quantity (or notional value) allowed in a single order, as a decimal string."""


class MaxNumAlgoOrdersFilter(TypedDict):
  """Maximum number of "algo" orders (STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT) this account may have open on the symbol."""

  filterType: Literal['MAX_NUM_ALGO_ORDERS']
  """Filter type discriminator."""
  maxNumAlgoOrders: int
  """Maximum number of open algo orders allowed on the symbol."""


class MaxNumIcebergOrdersFilter(TypedDict):
  """Maximum number of iceberg orders (icebergQty > 0) this account may have open on the symbol."""

  filterType: Literal['MAX_NUM_ICEBERG_ORDERS']
  """Filter type discriminator."""
  maxNumIcebergOrders: int
  """Maximum number of open iceberg orders allowed on the symbol."""


class MaxNumOrderAmendsFilter(TypedDict):
  """Maximum number of times an order can be amended on the symbol."""

  filterType: Literal['MAX_NUM_ORDER_AMENDS']
  """Filter type discriminator."""
  maxNumOrderAmends: int
  """Maximum number of amendments allowed on a single order."""


class MaxNumOrderListsFilter(TypedDict):
  """Maximum number of open order lists this account can have on the symbol (OTOCOs count as one order list)."""

  filterType: Literal['MAX_NUM_ORDER_LISTS']
  """Filter type discriminator."""
  maxNumOrderLists: int
  """Maximum number of open order lists allowed on the symbol."""


class MaxNumOrdersFilter(TypedDict):
  """Maximum number of orders this account may have open on the symbol (algo and normal orders both count)."""

  filterType: Literal['MAX_NUM_ORDERS']
  """Filter type discriminator."""
  maxNumOrders: int
  """Maximum number of open orders allowed on the symbol."""


class MaxPositionFilter(TypedDict):
  """Maximum position this account can have on the symbol's base asset (free + locked balance + open BUY order quantity). BUY orders are rejected if this would be exceeded."""

  filterType: Literal['MAX_POSITION']
  """Filter type discriminator."""
  maxPosition: str
  """Maximum base-asset position allowed, as a decimal string."""


class MinNotionalFilter(TypedDict):
  """Minimum notional (price * quantity) value allowed for an order on the symbol."""

  filterType: Literal['MIN_NOTIONAL']
  """Filter type discriminator."""
  minNotional: str
  """Minimum notional value allowed, as a decimal string."""
  applyToMarket: bool
  """Whether this filter also applies to MARKET orders."""
  avgPriceMins: int
  """Minutes of trade prices averaged for the reference price used in place of a MARKET order's price. `0` means the last price is used."""


class NotionalFilter(TypedDict):
  """Acceptable notional (price * quantity) range allowed for an order on the symbol."""

  filterType: Literal['NOTIONAL']
  """Filter type discriminator."""
  minNotional: str
  """Minimum notional value allowed, as a decimal string."""
  applyMinToMarket: bool
  """Whether `minNotional` applies to MARKET orders."""
  maxNotional: str
  """Maximum notional value allowed, as a decimal string."""
  applyMaxToMarket: bool
  """Whether `maxNotional` applies to MARKET orders."""
  avgPriceMins: int
  """Minutes of trade prices averaged for the reference price used in place of a MARKET order's price. `0` means the last price is used."""


class PercentPriceBySideFilter(TypedDict):
  """Valid order price range based on the average of previous trade prices, with separate bounds for BUY and SELL orders."""

  filterType: Literal['PERCENT_PRICE_BY_SIDE']
  """Filter type discriminator."""
  bidMultiplierUp: str
  """Upper multiplier applied to the reference price for BUY orders, as a decimal string."""
  bidMultiplierDown: str
  """Lower multiplier applied to the reference price for BUY orders, as a decimal string."""
  askMultiplierUp: str
  """Upper multiplier applied to the reference price for SELL orders, as a decimal string."""
  askMultiplierDown: str
  """Lower multiplier applied to the reference price for SELL orders, as a decimal string."""
  avgPriceMins: int
  """Minutes of trade prices averaged for the reference price when no reference price exists. `0` means the last price is used."""


class PercentPriceFilter(TypedDict):
  """Valid order price range based on the average of previous trade prices."""

  filterType: Literal['PERCENT_PRICE']
  """Filter type discriminator."""
  multiplierUp: str
  """Upper multiplier applied to the reference price, as a decimal string."""
  multiplierDown: str
  """Lower multiplier applied to the reference price, as a decimal string."""
  avgPriceMins: int
  """Minutes of trade prices averaged for the reference price when no reference price exists. `0` means the last price is used."""


class PriceFilter(TypedDict):
  """Price rules for the symbol. Any bound set to 0 disables that rule."""

  filterType: Literal['PRICE_FILTER']
  """Filter type discriminator."""
  minPrice: str
  """Minimum price/stopPrice allowed, as a decimal string. Disabled when `0`."""
  maxPrice: str
  """Maximum price/stopPrice allowed, as a decimal string. Disabled when `0`."""
  tickSize: str
  """Interval that price/stopPrice can be increased or decreased by, as a decimal string. Disabled when `0`."""


class TrailingDeltaFilter(TypedDict):
  """Minimum and maximum values allowed for a trailing stop order's `trailingDelta` parameter."""

  filterType: Literal['TRAILING_DELTA']
  """Filter type discriminator."""
  minTrailingAboveDelta: int
  """Minimum trailingDelta for STOP_LOSS/STOP_LOSS_LIMIT BUY and TAKE_PROFIT/TAKE_PROFIT_LIMIT SELL orders."""
  maxTrailingAboveDelta: int
  """Maximum trailingDelta for STOP_LOSS/STOP_LOSS_LIMIT BUY and TAKE_PROFIT/TAKE_PROFIT_LIMIT SELL orders."""
  minTrailingBelowDelta: int
  """Minimum trailingDelta for STOP_LOSS/STOP_LOSS_LIMIT SELL and TAKE_PROFIT/TAKE_PROFIT_LIMIT BUY orders."""
  maxTrailingBelowDelta: int
  """Maximum trailingDelta for STOP_LOSS/STOP_LOSS_LIMIT SELL and TAKE_PROFIT/TAKE_PROFIT_LIMIT BUY orders."""


class SymbolFilters(TypedDict):
  """Exchange, symbol, and asset filters relevant to this account on a symbol."""

  exchangeFilters: list[
    ExchangeMaxNumOrdersFilter
    | ExchangeMaxNumAlgoOrdersFilter
    | ExchangeMaxNumIcebergOrdersFilter
    | ExchangeMaxNumOrderListsFilter
  ]
  """Exchange-wide filters relevant to this account."""
  symbolFilters: list[
    PriceFilter
    | PercentPriceFilter
    | PercentPriceBySideFilter
    | LotSizeFilter
    | MinNotionalFilter
    | NotionalFilter
    | IcebergPartsFilter
    | MarketLotSizeFilter
    | MaxNumOrdersFilter
    | MaxNumAlgoOrdersFilter
    | MaxNumIcebergOrdersFilter
    | MaxPositionFilter
    | TrailingDeltaFilter
    | MaxNumOrderAmendsFilter
    | MaxNumOrderListsFilter
  ]
  """Symbol-specific filters relevant to this account on the given symbol."""
  assetFilters: list[MaxAssetFilter]
  """Asset-specific filters relevant to this account on the given symbol's base or quote asset."""


class MyFilters(RpcEndpoint):
  """Query relevant filters"""

  async def my_filters(
    self, *, symbol: str, validate: bool | None = None
  ) -> SymbolFilters:
    """Retrieve the list of exchange, symbol, and asset filters relevant to this account on a given symbol. This is the only endpoint that shows whether an account has a MAX_ASSET filter applied to it.

    Args:
      symbol: Symbol to query filters for.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = SymbolFilters
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/api/v3/myFilters', params=params, validator=_validator, validate=validate
    )
