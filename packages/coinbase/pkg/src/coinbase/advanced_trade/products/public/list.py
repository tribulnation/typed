from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class PublicProduct(TypedDict):
  """A tradable product on Advanced Trade."""

  product_id: str
  """Trading pair id, e.g. `BTC-USD`."""
  price: str
  """Current price, as a decimal string."""
  price_percentage_change_24h: NotRequired[str]
  """24h price change, as a percentage string."""
  volume_24h: NotRequired[str]
  """24h trading volume, as a decimal string."""
  volume_percentage_change_24h: NotRequired[str]
  """24h volume change, as a percentage string."""
  base_increment: str
  """Smallest allowed increment of the base currency."""
  quote_increment: str
  """Smallest allowed increment of the quote currency."""
  quote_min_size: NotRequired[str]
  """Minimum order size, quoted in the quote currency."""
  quote_max_size: NotRequired[str]
  """Maximum order size, quoted in the quote currency."""
  base_min_size: NotRequired[str]
  """Minimum order size, quoted in the base currency."""
  base_max_size: NotRequired[str]
  """Maximum order size, quoted in the base currency."""
  base_name: NotRequired[str]
  """Base currency display name."""
  quote_name: NotRequired[str]
  """Quote currency display name."""
  watched: NotRequired[bool]
  """Whether the calling context is watching this product."""
  is_disabled: NotRequired[bool]
  """Whether the product is disabled for trading."""
  new: NotRequired[bool]
  """Whether the product was recently listed."""
  status: str
  """Trading status. Observed example value `online`; not documented as an exhaustive enumeration by the fetched docs."""
  cancel_only: NotRequired[bool]
  """Whether the product only accepts order cancellations, not new orders."""
  limit_only: NotRequired[bool]
  """Whether the product only accepts limit orders."""
  post_only: NotRequired[bool]
  """Whether the product only accepts post-only orders."""
  trading_disabled: NotRequired[bool]
  """Whether trading is disabled for this product."""
  auction_mode: NotRequired[bool]
  """Whether the product is in auction mode."""
  product_type: Literal['SPOT', 'FUTURE', 'EQUITY', 'OPTION_GROUP', 'FUTURE_GROUP']
  """Product type."""
  quote_currency_id: NotRequired[str]
  """Quote currency code."""
  base_currency_id: NotRequired[str]
  """Base currency code."""
  mid_market_price: NotRequired[str]
  """Midpoint of best bid and best ask, as a decimal string."""
  alias: NotRequired[str]
  """This product's alias, if it has one."""
  alias_to: NotRequired[list[str]]
  """Other product ids this product is aliased to."""
  base_display_symbol: NotRequired[str]
  """Base currency symbol for display."""
  quote_display_symbol: NotRequired[str]
  """Quote currency symbol for display."""
  view_only: NotRequired[bool]
  """Whether the product is view-only (not tradable)."""
  price_increment: NotRequired[str]
  """Smallest allowed price increment."""
  display_name: NotRequired[str]
  """Product display name."""
  product_venue: NotRequired[str]
  """Internal venue routing this product trades on."""
  approximate_quote_24h_volume: NotRequired[str]
  """Approximate 24h volume, quoted in the quote currency."""
  new_at: NotRequired[str]
  """Listing time, ISO 8601."""
  market_cap: NotRequired[str]
  """Market capitalization of the base currency, as a decimal string."""
  icon_color: NotRequired[str]
  """Brand icon color."""
  icon_url: NotRequired[str]
  """Brand icon URL."""
  display_name_overwrite: NotRequired[str]
  """Override for `display_name`, when set."""
  about_description: NotRequired[str]
  """Long-form product description."""
  best_bid_price: NotRequired[str]
  """Current best bid price, as a decimal string."""
  best_ask_price: NotRequired[str]
  """Current best ask price, as a decimal string."""
  high_24h: NotRequired[str]
  """24h high price, as a decimal string."""
  low_24h: NotRequired[str]
  """24h low price, as a decimal string."""


class PublicProductsPagination(TypedDict):
  """Cursor pagination state for this page."""

  prev_cursor: NotRequired[str]
  """Cursor for the previous page."""
  next_cursor: NotRequired[str]
  """Cursor for the next page."""
  has_next: bool
  """Whether a next page exists."""
  has_prev: bool
  """Whether a previous page exists."""


class PublicProductsPage(TypedDict):
  products: list[PublicProduct]
  """The product catalog for this page."""
  num_products: int
  """Total number of products matching the query, across all pages."""
  pagination: NotRequired[PublicProductsPagination]


@dataclass(frozen=True, kw_only=True)
class List(RpcEndpoint):
  """`GET /api/v3/brokerage/market/products`."""

  async def list(
    self,
    *,
    limit: int | None = None,
    offset: int | None = None,
    product_type: Literal[
      'UNKNOWN_PRODUCT_TYPE', 'SPOT', 'FUTURE', 'EQUITY', 'OPTION_GROUP', 'FUTURE_GROUP'
    ]
    | None = None,
    product_ids: list[str] | None = None,
    contract_expiry_type: Literal[
      'UNKNOWN_CONTRACT_EXPIRY_TYPE', 'EXPIRING', 'PERPETUAL'
    ]
    | None = None,
    expiring_contract_status: Literal[
      'UNKNOWN_EXPIRING_CONTRACT_STATUS',
      'STATUS_UNEXPIRED',
      'STATUS_EXPIRED',
      'STATUS_ALL',
    ]
    | None = None,
    get_all_products: bool | None = None,
    products_sort_order: Literal[
      'PRODUCTS_SORT_ORDER_UNDEFINED',
      'PRODUCTS_SORT_ORDER_VOLUME_24H_DESCENDING',
      'PRODUCTS_SORT_ORDER_LIST_TIME_DESCENDING',
    ]
    | None = None,
    cursor: str | None = None,
    futures_underlying_type: Literal[
      'UNKNOWN_FUTURES_UNDERLYING_TYPE',
      'FUTURES_UNDERLYING_TYPE_SPOT',
      'FUTURES_UNDERLYING_TYPE_INDEX',
      'FUTURES_UNDERLYING_TYPE_EQUITY',
      'FUTURES_UNDERLYING_TYPE_EQUITY_INDEX',
      'FUTURES_UNDERLYING_TYPE_EQUITY_ETF',
      'FUTURES_UNDERLYING_TYPE_PREIPO',
      'FUTURES_UNDERLYING_TYPE_COMMOD',
      'FUTURES_UNDERLYING_TYPE_COMMOD_ETF',
      'FUTURES_UNDERLYING_TYPE_COMMOD_INDEX',
      'FUTURES_UNDERLYING_TYPE_ADR',
      'FUTURES_UNDERLYING_TYPE_FOREIGN_EQUITY',
      'FUTURES_UNDERLYING_TYPE_OTC',
    ]
    | None = None,
    user_country_code: str | None = None,
    expired: bool | None = None,
  ) -> PublicProductsPage:
    """List the public Advanced Trade product catalog. No authentication required — verified live by `clients/coinbase/spec/core.md` and the hand-written `AdvancedTrade.list_products` core method, which calls this via the unsigned `request()` path; see `upstream.md` for a docs-page discrepancy on this point.

    Args:
      limit: The number of products to be returned.
      offset: The number of products to skip before returning.
      product_type: Filter by product type.
      product_ids: Trading pairs to filter to, e.g. `BTC-USD`.
      contract_expiry_type: Only returns products matching this contract expiry type. Futures products only.
      expiring_contract_status: Filter by contract status.
      get_all_products: Return all products across all product types.
      products_sort_order: Sort order for the returned products.
      cursor: Base64-encoded pagination cursor.
      futures_underlying_type: Filter futures products by underlying type.
      user_country_code: The requesting user's country code, for country-specific display filtering.
      expired: Return recently expired instruments instead of active ones.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/public/list-public-products)
    """
    params = {}
    if limit is not None:
      params['limit'] = limit
    if offset is not None:
      params['offset'] = offset
    if product_type is not None:
      params['product_type'] = product_type
    if product_ids is not None:
      params['product_ids'] = product_ids
    if contract_expiry_type is not None:
      params['contract_expiry_type'] = contract_expiry_type
    if expiring_contract_status is not None:
      params['expiring_contract_status'] = expiring_contract_status
    if get_all_products is not None:
      params['get_all_products'] = get_all_products
    if products_sort_order is not None:
      params['products_sort_order'] = products_sort_order
    if cursor is not None:
      params['cursor'] = cursor
    if futures_underlying_type is not None:
      params['futures_underlying_type'] = futures_underlying_type
    if user_country_code is not None:
      params['user_country_code'] = user_country_code
    if expired is not None:
      params['expired'] = expired
    return await self.request(
      'GET',
      '/api/v3/brokerage/market/products',
      params=params,
      validator=validator(PublicProductsPage),
    )
