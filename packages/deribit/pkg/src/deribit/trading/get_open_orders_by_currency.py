"""`private/get_open_orders_by_currency` — `private/get_open_orders_by_currency`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class Order(TypedDict):
  order_id: str
  """Unique order identifier"""
  starbase_order_id: NotRequired[int]
  """Raw Starbase order id, in Starbase's own (non currency-prefixed) id namespace. Only present for orders matched on Starbase."""
  order_state: Literal[
    'open', 'filled', 'rejected', 'cancelled', 'untriggered', 'triggered'
  ]
  """Order state: `"open"`, `"filled"`, `"rejected"`, `"cancelled"`, `"untriggered"`"""
  order_type: Literal[
    'market',
    'limit',
    'stop_market',
    'stop_limit',
    'take_market',
    'take_limit',
    'trailing_stop',
  ]
  """Order type: `"limit"`, `"market"`, `"stop_limit"`, `"stop_market"`, `"take_limit"`, `"take_market"`, `"trailing_stop"`"""
  original_order_type: NotRequired[Literal['market', 'market_limit']]
  """Original order type. Optional field"""
  time_in_force: Literal[
    'good_til_cancelled', 'good_til_day', 'fill_or_kill', 'immediate_or_cancel'
  ]
  """Order time in force: `"good_til_cancelled"`, `"good_til_day"`, `"fill_or_kill"` or `"immediate_or_cancel"`"""
  is_rebalance: NotRequired[bool]
  """Optional (only for spot). `true` if order was automatically created during cross-collateral balance restoration"""
  is_liquidation: NotRequired[bool]
  """Optional (not added for spot). `true` if order was automatically created during liquidation"""
  instrument_name: str
  """Unique instrument identifier"""
  creation_timestamp: int
  """The timestamp (milliseconds since the Unix epoch)"""
  last_update_timestamp: int
  """The timestamp (milliseconds since the Unix epoch)"""
  starbase_last_update_timestamp: NotRequired[int]
  """The Starbase causal timestamp (nanoseconds since the Unix epoch) of the last book update that affected this order. Present only for orders placed in Starbase; not always available for direct access orders"""
  direction: Literal['buy', 'sell']
  """Direction: `buy`, or `sell`"""
  price: float | Literal['market_price']
  """Price in base currency or "market_price" in case of open trigger market orders"""
  label: str
  """User defined label (up to 64 characters)"""
  post_only: bool
  """`true` for post-only orders only"""
  reject_post_only: NotRequired[bool]
  """`true` if order has `reject_post_only` flag (field is present only when `post_only` is `true`)"""
  reduce_only: NotRequired[bool]
  """Optional (not added for spot). '`true` for reduce-only orders only'"""
  api: bool
  """`true` if created with API"""
  web: NotRequired[bool]
  """`true` if created via Deribit frontend (optional)"""
  mobile: NotRequired[bool]
  """Optional field with value `true` added only when created with Mobile Application"""
  refresh_amount: NotRequired[float]
  """The initial display amount of iceberg order. Iceberg order display amount will be refreshed to that value after match consuming actual display amount. Absent for other types of orders"""
  display_amount: NotRequired[float]
  """The actual display amount of iceberg order. Absent for other types of orders."""
  amount: NotRequired[float]
  """It represents the requested order size. For perpetual and inverse futures the amount is in USD units. For options and linear futures it is the underlying base currency coin."""
  contracts: NotRequired[float]
  """It represents the order size in contract units. (Optional, may be absent in historical data)."""
  filled_amount: NotRequired[float]
  """Filled amount of the order. For perpetual and futures the filled_amount is in USD units, for options - in units or corresponding cryptocurrency contracts, e.g., BTC or ETH."""
  average_price: NotRequired[float]
  """Average fill price of the order"""
  advanced: NotRequired[Literal['usd', 'implv']]
  """advanced type: `"usd"` or `"implv"` (Only for options; field is omitted if not applicable)."""
  implv: NotRequired[float]
  """Implied volatility in percent. (Only if `advanced="implv"`)"""
  usd: NotRequired[float]
  """Option price in USD (Only if `advanced="usd"`)"""
  triggered: NotRequired[bool]
  """Whether the trigger order has been triggered"""
  trigger: NotRequired[Literal['index_price', 'mark_price', 'last_price']]
  """Trigger type (only for trigger orders). Allowed values: `"index_price"`, `"mark_price"`, `"last_price"`."""
  trigger_price: NotRequired[float]
  """Trigger price (Only for future trigger orders)"""
  trigger_offset: NotRequired[float | None]
  """The maximum deviation from the price peak beyond which the order will be triggered (Only for trailing trigger orders)"""
  trigger_reference_price: NotRequired[float]
  """The price of the given trigger at the time when the order was placed (Only for trailing trigger orders)"""
  block_trade: NotRequired[bool]
  """`true` if order made from block_trade trade, added only in that case."""
  mmp: NotRequired[bool]
  """`true` if the order is a MMP order, otherwise `false`."""
  risk_reducing: NotRequired[bool]
  """`true` if the order is marked by the platform as a risk reducing order (can apply only to orders placed by PM users), otherwise `false`."""
  replaced: NotRequired[bool]
  """`true` if the order was edited (by user or - in case of advanced options orders - by pricing engine), otherwise `false`."""
  auto_replaced: NotRequired[bool]
  """Options, advanced orders only - `true` if last modification of the order was performed by the pricing engine, otherwise `false`."""
  quote: NotRequired[bool]
  """If order is a quote. Present only if true."""
  mmp_group: NotRequired[str]
  """Name of the MMP group supplied in the `private/mass_quote` request. Only present for quote orders."""
  quote_set_id: NotRequired[str]
  """Identifier of the QuoteSet supplied in the `private/mass_quote` request. Only present for quote orders."""
  quote_id: NotRequired[str]
  """The same QuoteID as supplied in the `private/mass_quote` request. Only present for quote orders."""
  trigger_order_id: NotRequired[str]
  """Id of the trigger order that created the order (Only for orders that were created by triggered orders)."""
  combo_order_id: NotRequired[str]
  """Id of the combo order that created this order (only present for orders that were created as legs of a combo order)."""
  app_name: NotRequired[str]
  """The name of the application that placed the order on behalf of the user (optional)."""
  mmp_cancelled: NotRequired[bool]
  """`true` if order was cancelled by mmp trigger (optional)"""
  cancel_reason: NotRequired[
    Literal[
      'user_request',
      'autoliquidation',
      'cancel_on_disconnect',
      'risk_mitigation',
      'pme_risk_reduction',
      'pme_account_locked',
      'position_locked',
      'mmp_trigger',
      'mmp_config_curtailment',
      'edit_post_only_reject',
      'oco_other_closed',
      'oto_primary_closed',
      'settlement',
    ]
  ]
  """Enumerated reason behind cancel `"user_request"`, `"autoliquidation"`, `"cancel_on_disconnect"`, `"risk_mitigation"`, `"pme_risk_reduction"` (portfolio margining risk reduction), `"pme_account_locked"` (portfolio margining account locked per currency), `"position_locked"`, `"mmp_trigger"` (market maker protection), `"mmp_config_curtailment"` (market maker configured quantity decreased), `"edit_post_only_reject"` (cancelled on edit because of `reject_post_only` setting), `"oco_other_closed"` (the oco order linked to this order was closed), `"oto_primary_closed"` (the oto primary order that was going to trigger this order was cancelled), `"settlement"` (closed because of a settlement)"""
  oto_order_ids: NotRequired[list[str]]
  """The Ids of the orders that will be triggered if the order is filled"""
  trigger_fill_condition: NotRequired[
    Literal['first_hit', 'complete_fill', 'incremental']
  ]
  """The fill condition of the linked order (Only for linked order types), default: `first_hit`.

  - `"first_hit"` - any execution of the primary order will fully cancel/place all secondary orders.
 - `"complete_fill"` - a complete execution (meaning the primary order no longer exists) will cancel/place the secondary orders.
 - `"incremental"` - any fill of the primary order will cause proportional partial cancellation/placement of the secondary order. The amount that will be subtracted/added to the secondary order will be rounded down to the contract size."""
  oco_ref: NotRequired[str]
  """Unique reference that identifies a one_cancels_others (OCO) pair."""
  primary_order_id: NotRequired[str]
  """Unique order identifier"""
  is_secondary_oto: NotRequired[bool]
  """`true` if the order is an order that can be triggered by another order, otherwise not present."""
  is_primary_otoco: NotRequired[bool]
  """`true` if the order is an order that can trigger an OCO pair, otherwise not present."""
  user_id: NotRequired[int]
  """Id of the account this order/position belongs to."""


validate_get_open_orders_by_currency = validator[list[Order]](list[Order])


class GetOpenOrdersByCurrency(RpcEndpoint):
  """`private/get_open_orders_by_currency`."""

  async def get_open_orders_by_currency(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    kind: Literal['future', 'option', 'spot', 'future_combo', 'option_combo']
    | None = None,
    type: Literal[
      'all',
      'limit',
      'trigger_all',
      'stop_all',
      'stop_limit',
      'stop_market',
      'take_all',
      'take_limit',
      'take_market',
      'trailing_all',
      'trailing_stop',
    ]
    | None = None,
    validate: bool | None = None,
  ) -> list[Order]:
    """Retrieves a list of all open orders for a specific currency. Open orders are orders that have been placed but not yet filled or cancelled.

    Results can be filtered by instrument kind and order type. This method provides a view of all active orders within a currency.

    Args:
      currency: The currency symbol
      kind: Instrument kind, if not provided instruments of all kinds are considered
      type: Order type, default - `all`
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/trading/private-get_open_orders_by_currency)
    """
    params: dict = {
      'currency': currency,
    }
    if kind is not None:
      params['kind'] = kind
    if type is not None:
      params['type'] = type
    return await self.authed_request(
      'private/get_open_orders_by_currency',
      params=params,
      validator=validate_get_open_orders_by_currency,
      validate=validate,
    )
