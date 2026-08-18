"""`user.trades.{kind}.{currency}.{interval}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class ClientInfo(TypedDict):
  """Optional client allocation info for brokers."""

  client_id: NotRequired[int]
  """ID of a client; available to broker. Represents a group of users under a common name."""
  client_link_id: NotRequired[int]
  """ID assigned to a single user in a client; available to broker."""
  name: NotRequired[str]
  """Name of the linked user within the client; available to broker."""


class TradeAllocations(TypedDict):
  """List of allocations for Block RFQ pre-allocation. Each allocation specifies `user_id`, `amount`, and `fee` for the allocated part of the trade. For broker client allocations, a `client_info` object will be included."""

  user_id: NotRequired[int]
  """User ID to which part of the trade is allocated. For brokers the User ID is obstructed."""
  amount: float
  """Amount allocated to this user."""
  fee: float
  """Fee for the allocated part of the trade."""
  client_info: NotRequired[ClientInfo]


class TradesByKindCurrencyUpdate(TypedDict):
  """Message schema for `user.trades.(kind).(currency).(interval)` subscription - contains the data payload"""

  trade_id: str
  """Unique (per currency) trade identifier"""
  trade_seq: int
  """The sequence number of the trade within instrument"""
  instrument_name: str
  """Unique instrument identifier"""
  timestamp: int
  """The timestamp of the trade (milliseconds since the UNIX epoch)"""
  starbase_timestamp: NotRequired[int]
  """The Starbase causal timestamp of the trade (nanoseconds since the Unix epoch)"""
  order_type: NotRequired[Literal['limit', 'market', 'liquidation']]
  """Order type: `"limit`, `"market"`, or `"liquidation"`"""
  original_order_type: NotRequired[Literal['market', 'market_limit']]
  """Original API order type when an order is represented internally as a limit order. For example, Starbase market orders use `"limit"` as `order_type` with `"market"` in this optional field."""
  advanced: NotRequired[Literal['usd', 'implv']]
  """Advanced type of user order: `"usd"` or `"implv"` (only for options; omitted if not applicable)"""
  order_id: str
  """Id of the user order (maker or taker), i.e. subscriber's order id that took part in the trade"""
  matching_id: str
  """Always `null`"""
  direction: Literal['buy', 'sell']
  """Direction: `buy`, or `sell`"""
  tick_direction: Literal[0, 1, 2, 3]
  """Direction of the "tick" (`0` = Plus Tick, `1` = Zero-Plus Tick, `2` = Minus Tick, `3` = Zero-Minus Tick)."""
  index_price: float
  """Index Price at the moment of trade"""
  price: float
  """Price in base currency"""
  amount: float
  """Trade amount. For perpetual and inverse futures the amount is in USD units. For options and linear futures it is the underlying base currency coin."""
  contracts: NotRequired[float]
  """Trade size in contract units (optional, may be absent in historical trades)"""
  iv: NotRequired[float]
  """Option implied volatility for the price (Option only)"""
  underlying_price: NotRequired[float]
  """Underlying price for implied volatility calculations (Options only)"""
  liquidation: NotRequired[Literal['M', 'T', 'MT']]
  """Optional field (only for trades caused by liquidation): `"M"` when maker side of trade was under liquidation, `"T"` when taker side was under liquidation, `"MT"` when both sides of trade were under liquidation"""
  liquidity: NotRequired[Literal['M', 'T']]
  """Describes what was role of users order: `"M"` when it was maker order, `"T"` when it was taker order"""
  fee: float
  """User's fee in units of the specified `fee_currency`"""
  fee_currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR']
  """Currency, i.e `"BTC"`, `"ETH"`, `"USDC"`"""
  label: NotRequired[str]
  """User defined label (presented only when previously set for order by user)"""
  state: Literal['open', 'filled', 'rejected', 'cancelled', 'untriggered', 'archive']
  """Order state: `"open"`, `"filled"`, `"rejected"`, `"cancelled"`, `"untriggered"` or `"archive"` (if order was archived)"""
  block_trade_id: NotRequired[str]
  """Block trade id - when trade was part of a block trade"""
  block_trade_leg_count: NotRequired[int]
  """Block trade leg count - when trade was part of a block trade"""
  block_rfq_id: NotRequired[int]
  """ID of the Block RFQ - when trade was part of the Block RFQ"""
  block_rfq_quote_id: NotRequired[int]
  """ID of the Block RFQ quote - when trade was part of the Block RFQ"""
  reduce_only: NotRequired[str]
  """`true` if user order is reduce-only"""
  post_only: NotRequired[str]
  """`true` if user order is post-only"""
  mmp: NotRequired[bool]
  """`true` if user order is MMP"""
  risk_reducing: NotRequired[bool]
  """`true` if user order is marked by the platform as a risk reducing order (can apply only to orders placed by PM users)"""
  api: NotRequired[bool]
  """`true` if user order was created with API"""
  profit_loss: NotRequired[float]
  """Profit and loss in base currency."""
  mark_price: float
  """Mark Price at the moment of trade"""
  legs: NotRequired[list[dict[str, Any]]]
  """Optional field containing leg trades if trade is a combo trade (present when querying for **only** combo trades and in `combo_trades` events). Each leg trade has the same fields as a top-level user trade, including `starbase_match_id` and `starbase_timestamp` when matched via Starbase."""
  combo_id: NotRequired[str]
  """Optional field containing combo instrument name if the trade is a combo trade"""
  combo_trade_id: NotRequired[str]
  """Optional field containing combo trade identifier if the trade is a combo trade"""
  starbase_match_id: NotRequired[int]
  """Optional field containing the Starbase match identifier (present only for trades matched via Starbase)"""
  quote_set_id: NotRequired[str]
  """QuoteSet of the user order (optional, present only for orders placed with `private/mass_quote`)"""
  quote_id: NotRequired[str]
  """QuoteID of the user order (optional, present only for orders placed with `private/mass_quote`)"""
  trade_allocations: NotRequired[TradeAllocations]


validate_trades_by_kind_currency = validator[TradesByKindCurrencyUpdate](
  TradesByKindCurrencyUpdate
)


class TradesByKindCurrency(StreamEndpoint):
  """`user.trades.{kind}.{currency}.{interval}` subscription."""

  def trades_by_kind_currency(
    self,
    kind: Literal['future', 'option', 'spot', 'future_combo', 'option_combo'],
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any'],
    interval: Literal['raw', '100ms', 'agg2'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[TradesByKindCurrencyUpdate, Any, Any]:
    """User trade notifications across all instruments for a given kind and currency.

    Receive a consolidated stream of your private trades across all instruments matching the specified `kind` and `currency`. The `interval` controls aggregation frequency.

    **Block RFQ trades:** Trades resulting from Block RFQ execution are included in this channel. See `user.trades.{instrument_name}.{interval}` for the complete list of Block RFQ-specific fields.

    Args:
      kind: Instrument kind

    **Allowed values:** `future`, `option`, `spot`, `future_combo`, `option_combo`
      currency: Currency code or `any` for all

    **Allowed values:** `BTC`, `ETH`, `USDC`, `USDT`, `EURR`, `any`
      interval: Frequency of notifications. Events will be aggregated over this interval. The value `raw` means no aggregation will be applied **(Please note that `raw` interval is only available to authorized users)**

    **Allowed values:** `raw`, `100ms`, `agg2`
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/subscriptions/user-trades-kind-currency-interval)
    """
    channel = f'user.trades.{kind}.{currency}.{interval}'
    return self.authed_subscribe(
      channel, validator=validate_trades_by_kind_currency, validate=validate
    )
