from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Any, Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class Product(TypedDict):
  """A tradable Advanced Trade product (spot pair, future, or equity)."""

  product_id: str
  """The trading pair, e.g. `BTC-USD`."""
  price: str
  """Current price in quote currency."""
  price_percentage_change_24h: str
  """Price change percent over the last 24 hours."""
  volume_24h: str
  """Trading volume over the last 24 hours."""
  volume_percentage_change_24h: str
  """Volume change percent over the last 24 hours."""
  base_increment: str
  """Minimum base currency amount change."""
  quote_increment: str
  """Minimum quote currency amount change."""
  quote_min_size: str
  """Minimum order size in quote currency."""
  quote_max_size: str
  """Maximum order size in quote currency."""
  base_min_size: str
  """Minimum order size in base currency."""
  base_max_size: str
  """Maximum order size in base currency."""
  base_name: str
  """Name of the base currency."""
  quote_name: str
  """Name of the quote currency."""
  watched: bool
  """Whether the product is on the caller's watchlist."""
  is_disabled: bool
  """Whether the product is disabled for trading."""
  new: bool
  """Whether the product is newly listed."""
  status: str
  """Status of the product."""
  cancel_only: bool
  """Whether orders on this product can only be cancelled."""
  limit_only: bool
  """Whether only limit orders are allowed on this product."""
  post_only: bool
  """Whether orders on this product can only be posted."""
  trading_disabled: bool
  """Whether trading is disabled for this product market-wide."""
  auction_mode: bool
  """Whether the product is in auction mode."""
  base_display_symbol: str
  """Display symbol for the base currency."""
  quote_display_symbol: str
  """Display symbol for the quote currency."""
  product_type: NotRequired[
    Literal[
      'UNKNOWN_PRODUCT_TYPE', 'SPOT', 'FUTURE', 'EQUITY', 'OPTION_GROUP', 'FUTURE_GROUP'
    ]
  ]
  """Product type."""
  quote_currency_id: NotRequired[str]
  """Symbol of the quote currency."""
  base_currency_id: NotRequired[str]
  """Symbol of the base currency."""
  mid_market_price: NotRequired[str]
  """Bid-ask spread midpoint."""
  alias: NotRequired[str]
  """Product id this product serves as a unified-book alias for."""
  alias_to: NotRequired[list[str]]
  """Product ids that alias to this product."""
  view_only: NotRequired[bool]
  """Tradability/expiration status of the product."""
  price_increment: NotRequired[str]
  """Minimum price change."""
  display_name: NotRequired[str]
  """Display name for the product."""
  approximate_quote_24h_volume: NotRequired[str]
  """24h volume in the current quote currency."""
  new_at: NotRequired[str]
  """Listing timestamp, when the product carries a 'new' tag."""
  market_cap: NotRequired[str]
  """Market capitalization of the base asset."""
  icon_color: NotRequired[str]
  """Color used to display the product icon."""
  icon_url: NotRequired[str]
  """URL to the product icon image."""
  display_name_overwrite: NotRequired[str]
  """Alternative display name for the product."""
  about_description: NotRequired[str]
  """Description shown in the product's about section."""
  best_bid_price: NotRequired[str]
  """Current best bid price."""
  best_ask_price: NotRequired[str]
  """Current best ask price."""
  high_24h: NotRequired[str]
  """Highest price over the last 24 hours."""
  low_24h: NotRequired[str]
  """Lowest price over the last 24 hours."""
  product_venue: NotRequired[Literal['UNKNOWN_VENUE_TYPE', 'CBE', 'FCM', 'INTX']]
  """Venue the product trades on."""
  fcm_trading_session_details: NotRequired[dict[str, Any] | None]
  """FCM (futures) trading session metadata, populated when `product_type` is `FUTURE`; `null` otherwise (verified live for SPOT products)."""
  future_product_details: NotRequired[dict[str, Any]]
  """Futures-specific product metadata, populated when `product_type` is `FUTURE`."""
  equity_product_details: NotRequired[dict[str, Any]]
  """Equity-specific product metadata, populated when `product_type` is `EQUITY`."""


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /api/v3/brokerage/products/{product_id}`."""

  async def __call__(
    self,
    product_id: str,
    *,
    get_tradability_status: bool | None = None,
  ) -> Product:
    """Get one product by id.

    Args:
      product_id: The trading pair, e.g. `BTC-USD`.
      get_tradability_status: Populate `view_only` with tradability status; SPOT products only.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/products/get-product)
    """
    params = {}
    if get_tradability_status is not None:
      params['get_tradability_status'] = get_tradability_status
    return await self.authed_request(
      'GET',
      f'/api/v3/brokerage/products/{product_id}',
      params=params,
      validator=validator(Product),
    )
