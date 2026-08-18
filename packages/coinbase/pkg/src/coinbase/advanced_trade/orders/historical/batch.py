from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class AmountAttachedOrderConfigurationAnyOf0MarketMarketIocCurrencySizeAnyOf0(
  TypedDict
):
  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class AmountAttachedOrderConfigurationAnyOf3LimitLimitGtcCurrencySizeAnyOf0(TypedDict):
  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class AmountAttachedOrderConfigurationAnyOf4LimitLimitGtdCurrencySize(TypedDict):
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""

  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class AmountOrderConfigurationAnyOf0MarketMarketIocCurrencySizeAnyOf0(TypedDict):
  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class AmountOrderConfigurationAnyOf3LimitLimitGtcCurrencySizeAnyOf0(TypedDict):
  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class AmountOrderConfigurationAnyOf4LimitLimitGtdCurrencySize(TypedDict):
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""

  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class AmountOutstandingHoldAmountNativeAnyOf0(TypedDict):
  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class AmountTotalFeesNativeAnyOf0(TypedDict):
  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class AmountTotalValueAfterFeesNativeAnyOf0(TypedDict):
  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class CommissionDetailTotal(TypedDict):
  """Breakdown of commission charged."""

  total_commission: NotRequired[str]
  """Sum of all commission components charged on the order."""
  gst_commission: NotRequired[str]
  """Goods and Services Tax (GST) portion of the commission."""
  withholding_commission: NotRequired[str]
  """Tax withholding portion of the commission."""
  client_commission: NotRequired[str]
  """Client commission on the trade."""
  venue_commission: NotRequired[str]
  """Venue commission."""
  regulatory_commission: NotRequired[str]
  """Regulatory commission."""
  clearing_commission: NotRequired[str]
  """Clearing commission."""


class Edit0(TypedDict):
  price: NotRequired[str]
  """Order price at the time of this edit."""
  size: NotRequired[str]
  """Order size at the time of this edit."""
  replace_accept_timestamp: NotRequired[str]
  """RFC3339 time the edit was accepted."""


class EditItem(TypedDict):
  """One historical edit applied to an order."""

  price: NotRequired[str]
  """Order price at the time of this edit."""
  size: NotRequired[str]
  """Order size at the time of this edit."""
  replace_accept_timestamp: NotRequired[str]
  """RFC3339 time the edit was accepted."""


class EquityOrderProductDetails(TypedDict):
  """Equity-specific product details."""

  base_cbrn: NotRequired[str]
  """CBRN identifier for the equity."""
  ticker: NotRequired[str]
  """Display ticker for the equity."""
  quote_id: NotRequired[str]
  """Quote identifier for the equity."""


class LimitLimitFokAttachedOrderConfigurationAnyOf5LimitLimitFok(TypedDict):
  """LimitLimitFok fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""


class LimitLimitFokOrderConfigurationAnyOf5LimitLimitFok(TypedDict):
  """LimitLimitFok fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""


class MarketMarketFokAttachedOrderConfigurationAnyOf1MarketMarketFok(TypedDict):
  """MarketMarketFok fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""


class MarketMarketFokOrderConfigurationAnyOf1MarketMarketFok(TypedDict):
  """MarketMarketFok fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""


class ScaledOrderLegAttachedOrderConfigurationAnyOf11ScaledLimitGtcOrdersItem(
  TypedDict
):
  """One child limit order in a scaled order."""

  base_size: NotRequired[str]
  """Base-currency amount for this leg."""
  limit_price: NotRequired[str]
  """Limit price for this leg."""


class ScaledOrderLegOrderConfigurationAnyOf11ScaledLimitGtcOrdersItem(TypedDict):
  """One child limit order in a scaled order."""

  base_size: NotRequired[str]
  """Base-currency amount for this leg."""
  limit_price: NotRequired[str]
  """Limit price for this leg."""


class SorLimitIocAttachedOrderConfigurationAnyOf2SorLimitIoc(TypedDict):
  """SorLimitIoc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""


class SorLimitIocOrderConfigurationAnyOf2SorLimitIoc(TypedDict):
  """SorLimitIoc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""


class StopLimitStopLimitGtcAttachedOrderConfigurationAnyOf7StopLimitStopLimitGtc(
  TypedDict
):
  """StopLimitStopLimitGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_price: str
  """Last trade price that triggers the order."""
  stop_direction: Literal['STOP_DIRECTION_STOP_UP', 'STOP_DIRECTION_STOP_DOWN']
  """Which way the last trade price must cross `stop_price` to trigger."""


class StopLimitStopLimitGtcOrderConfigurationAnyOf7StopLimitStopLimitGtc(TypedDict):
  """StopLimitStopLimitGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_price: str
  """Last trade price that triggers the order."""
  stop_direction: Literal['STOP_DIRECTION_STOP_UP', 'STOP_DIRECTION_STOP_DOWN']
  """Which way the last trade price must cross `stop_price` to trigger."""


class StopLimitStopLimitGtdAttachedOrderConfigurationAnyOf8StopLimitStopLimitGtd(
  TypedDict
):
  """StopLimitStopLimitGtd fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_price: str
  """Last trade price that triggers the order."""
  end_time: str
  """RFC3339 time after which the order expires if unfilled."""
  stop_direction: Literal['STOP_DIRECTION_STOP_UP', 'STOP_DIRECTION_STOP_DOWN']
  """Which way the last trade price must cross `stop_price` to trigger."""


class StopLimitStopLimitGtdOrderConfigurationAnyOf8StopLimitStopLimitGtd(TypedDict):
  """StopLimitStopLimitGtd fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_price: str
  """Last trade price that triggers the order."""
  end_time: str
  """RFC3339 time after which the order expires if unfilled."""
  stop_direction: Literal['STOP_DIRECTION_STOP_UP', 'STOP_DIRECTION_STOP_DOWN']
  """Which way the last trade price must cross `stop_price` to trigger."""


class TriggerBracketGtcAttachedOrderConfigurationAnyOf9TriggerBracketGtc(TypedDict):
  """TriggerBracketGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_trigger_price: str
  """Price (in quote currency) at which the position is exited; the resulting stop-limit order's limit price is 5% beyond it (higher for buys, lower for sells)."""


class TriggerBracketGtcOrderConfigurationAnyOf9TriggerBracketGtc(TypedDict):
  """TriggerBracketGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_trigger_price: str
  """Price (in quote currency) at which the position is exited; the resulting stop-limit order's limit price is 5% beyond it (higher for buys, lower for sells)."""


class TriggerBracketGtdAttachedOrderConfigurationAnyOf10TriggerBracketGtd(TypedDict):
  """TriggerBracketGtd fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_trigger_price: str
  """Price (in quote currency) at which the position is exited; the resulting stop-limit order's limit price is 5% beyond it (higher for buys, lower for sells)."""
  end_time: str
  """RFC3339 time after which the order expires if unfilled."""


class TriggerBracketGtdOrderConfigurationAnyOf10TriggerBracketGtd(TypedDict):
  """TriggerBracketGtd fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_trigger_price: str
  """Price (in quote currency) at which the position is exited; the resulting stop-limit order's limit price is 5% beyond it (higher for buys, lower for sells)."""
  end_time: str
  """RFC3339 time after which the order expires if unfilled."""


class TwapLimitGtdAttachedOrderConfigurationAnyOf6TwapLimitGtd(TypedDict):
  """TwapLimitGtd fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  start_time: str
  """RFC3339 time execution begins."""
  end_time: str
  """RFC3339 time execution ends."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  number_buckets: str
  """Number of suborders to split execution into."""
  bucket_size: str
  """Size of each suborder; `bucket_size * number_buckets` should equal the total order size."""
  bucket_duration: str
  """Duration each suborder executes over, e.g. `"300s"`."""


class TwapLimitGtdOrderConfigurationAnyOf6TwapLimitGtd(TypedDict):
  """TwapLimitGtd fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  start_time: str
  """RFC3339 time execution begins."""
  end_time: str
  """RFC3339 time execution ends."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  number_buckets: str
  """Number of suborders to split execution into."""
  bucket_size: str
  """Size of each suborder; `bucket_size * number_buckets` should equal the total order size."""
  bucket_duration: str
  """Duration each suborder executes over, e.g. `"300s"`."""


class LimitLimitFokConfigurationAttachedOrderConfigurationAnyOf5(TypedDict):
  """Limit order, fill-or-kill: posts only if it fills immediately and completely."""

  limit_limit_fok: LimitLimitFokAttachedOrderConfigurationAnyOf5LimitLimitFok


class LimitLimitFokConfigurationOrderConfigurationAnyOf5(TypedDict):
  """Limit order, fill-or-kill: posts only if it fills immediately and completely."""

  limit_limit_fok: LimitLimitFokOrderConfigurationAnyOf5LimitLimitFok


class LimitLimitGtcAttachedOrderConfigurationAnyOf3LimitLimitGtc(TypedDict):
  """LimitLimitGtc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  post_only: NotRequired[bool]
  """Only post liquidity; reject rather than take."""
  currency_size: NotRequired[
    AmountAttachedOrderConfigurationAnyOf3LimitLimitGtcCurrencySizeAnyOf0 | None
  ]
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""
  rfq_disabled: NotRequired[bool]
  """Whether RFQ (request-for-quote) execution is disabled for this order."""
  reduce_only: NotRequired[bool]
  """Whether the order can only reduce an existing position."""
  oco_ref: NotRequired[str]
  """Reference id of a linked one-cancels-other order. Empty when none."""


class LimitLimitGtcOrderConfigurationAnyOf3LimitLimitGtc(TypedDict):
  """LimitLimitGtc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  post_only: NotRequired[bool]
  """Only post liquidity; reject rather than take."""
  currency_size: NotRequired[
    AmountOrderConfigurationAnyOf3LimitLimitGtcCurrencySizeAnyOf0 | None
  ]
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""
  rfq_disabled: NotRequired[bool]
  """Whether RFQ (request-for-quote) execution is disabled for this order."""
  reduce_only: NotRequired[bool]
  """Whether the order can only reduce an existing position."""
  oco_ref: NotRequired[str]
  """Reference id of a linked one-cancels-other order. Empty when none."""


class LimitLimitGtdAttachedOrderConfigurationAnyOf4LimitLimitGtd(TypedDict):
  """LimitLimitGtd fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  end_time: str
  """RFC3339 time after which the order expires if unfilled."""
  post_only: NotRequired[bool]
  """Only post liquidity; reject rather than take."""
  currency_size: NotRequired[
    AmountAttachedOrderConfigurationAnyOf4LimitLimitGtdCurrencySize
  ]


class LimitLimitGtdOrderConfigurationAnyOf4LimitLimitGtd(TypedDict):
  """LimitLimitGtd fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  end_time: str
  """RFC3339 time after which the order expires if unfilled."""
  post_only: NotRequired[bool]
  """Only post liquidity; reject rather than take."""
  currency_size: NotRequired[AmountOrderConfigurationAnyOf4LimitLimitGtdCurrencySize]


class MarketMarketFokConfigurationAttachedOrderConfigurationAnyOf1(TypedDict):
  """Market order, fill-or-kill: posts only if it fills immediately and completely."""

  market_market_fok: MarketMarketFokAttachedOrderConfigurationAnyOf1MarketMarketFok


class MarketMarketFokConfigurationOrderConfigurationAnyOf1(TypedDict):
  """Market order, fill-or-kill: posts only if it fills immediately and completely."""

  market_market_fok: MarketMarketFokOrderConfigurationAnyOf1MarketMarketFok


class MarketMarketIocAttachedOrderConfigurationAnyOf0MarketMarketIoc(TypedDict):
  """MarketMarketIoc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  currency_size: NotRequired[
    AmountAttachedOrderConfigurationAnyOf0MarketMarketIocCurrencySizeAnyOf0 | None
  ]
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""
  rfq_enabled: NotRequired[bool]
  """Whether RFQ (request-for-quote) execution is enabled for this order."""
  rfq_disabled: NotRequired[bool]
  """Whether RFQ (request-for-quote) execution is disabled for this order."""
  reduce_only: NotRequired[bool]
  """Whether the order can only reduce an existing position."""
  oco_ref: NotRequired[str]
  """Reference id of a linked one-cancels-other order. Empty when none."""


class MarketMarketIocOrderConfigurationAnyOf0MarketMarketIoc(TypedDict):
  """MarketMarketIoc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  currency_size: NotRequired[
    AmountOrderConfigurationAnyOf0MarketMarketIocCurrencySizeAnyOf0 | None
  ]
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""
  rfq_enabled: NotRequired[bool]
  """Whether RFQ (request-for-quote) execution is enabled for this order."""
  rfq_disabled: NotRequired[bool]
  """Whether RFQ (request-for-quote) execution is disabled for this order."""
  reduce_only: NotRequired[bool]
  """Whether the order can only reduce an existing position."""
  oco_ref: NotRequired[str]
  """Reference id of a linked one-cancels-other order. Empty when none."""


class ProductDetails(TypedDict):
  equity_details: NotRequired[EquityOrderProductDetails]


class ScaledLimitGtcAttachedOrderConfigurationAnyOf11ScaledLimitGtc(TypedDict):
  """ScaledLimitGtc fields."""

  orders: NotRequired[
    list[ScaledOrderLegAttachedOrderConfigurationAnyOf11ScaledLimitGtcOrdersItem]
  ]
  """Explicit child-order legs, when `price_distribution`/`size_distribution` is `CUSTOM_*`."""
  quote_size: NotRequired[str]
  """Total quote-currency amount across all legs. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Total base-currency amount across all legs. One of `quote_size`/`base_size` is required."""
  num_orders: int
  """Number of child orders to split execution into."""
  min_price: str
  """Lowest limit price in the ladder."""
  max_price: str
  """Highest limit price in the ladder."""
  price_distribution: Literal[
    'FLAT', 'LINEAR_INCREASING', 'LINEAR_DECREASING', 'CUSTOM_PRICE_DISTRIBUTION'
  ]
  """How child order prices are spread across the range."""
  size_distribution: Literal[
    'UNKNOWN_DISTRIBUTION',
    'INCREASING',
    'DECREASING',
    'EVENLY_SPLIT',
    'CUSTOM_SIZE_DISTRIBUTION',
  ]
  """How child order sizes are spread across the range."""
  size_diff: NotRequired[str]
  """Size delta between consecutive legs, for `LINEAR_*` size distributions."""
  size_ratio: NotRequired[str]
  """Size ratio between consecutive legs, for `LINEAR_*` size distributions."""


class ScaledLimitGtcOrderConfigurationAnyOf11ScaledLimitGtc(TypedDict):
  """ScaledLimitGtc fields."""

  orders: NotRequired[
    list[ScaledOrderLegOrderConfigurationAnyOf11ScaledLimitGtcOrdersItem]
  ]
  """Explicit child-order legs, when `price_distribution`/`size_distribution` is `CUSTOM_*`."""
  quote_size: NotRequired[str]
  """Total quote-currency amount across all legs. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Total base-currency amount across all legs. One of `quote_size`/`base_size` is required."""
  num_orders: int
  """Number of child orders to split execution into."""
  min_price: str
  """Lowest limit price in the ladder."""
  max_price: str
  """Highest limit price in the ladder."""
  price_distribution: Literal[
    'FLAT', 'LINEAR_INCREASING', 'LINEAR_DECREASING', 'CUSTOM_PRICE_DISTRIBUTION'
  ]
  """How child order prices are spread across the range."""
  size_distribution: Literal[
    'UNKNOWN_DISTRIBUTION',
    'INCREASING',
    'DECREASING',
    'EVENLY_SPLIT',
    'CUSTOM_SIZE_DISTRIBUTION',
  ]
  """How child order sizes are spread across the range."""
  size_diff: NotRequired[str]
  """Size delta between consecutive legs, for `LINEAR_*` size distributions."""
  size_ratio: NotRequired[str]
  """Size ratio between consecutive legs, for `LINEAR_*` size distributions."""


class SorLimitIocConfigurationAttachedOrderConfigurationAnyOf2(TypedDict):
  """Smart-order-routed limit order, immediate-or-cancel: posts only if it fills immediately, any unfilled remainder is cancelled."""

  sor_limit_ioc: SorLimitIocAttachedOrderConfigurationAnyOf2SorLimitIoc


class SorLimitIocConfigurationOrderConfigurationAnyOf2(TypedDict):
  """Smart-order-routed limit order, immediate-or-cancel: posts only if it fills immediately, any unfilled remainder is cancelled."""

  sor_limit_ioc: SorLimitIocOrderConfigurationAnyOf2SorLimitIoc


class StopLimitStopLimitGtcConfigurationAttachedOrderConfigurationAnyOf7(TypedDict):
  """Stop-limit order, good-till-cancelled: becomes a limit order once the last trade price crosses `stop_price`."""

  stop_limit_stop_limit_gtc: (
    StopLimitStopLimitGtcAttachedOrderConfigurationAnyOf7StopLimitStopLimitGtc
  )


class StopLimitStopLimitGtcConfigurationOrderConfigurationAnyOf7(TypedDict):
  """Stop-limit order, good-till-cancelled: becomes a limit order once the last trade price crosses `stop_price`."""

  stop_limit_stop_limit_gtc: (
    StopLimitStopLimitGtcOrderConfigurationAnyOf7StopLimitStopLimitGtc
  )


class StopLimitStopLimitGtdConfigurationAttachedOrderConfigurationAnyOf8(TypedDict):
  """Stop-limit order, good-till-date: becomes a limit order once the last trade price crosses `stop_price`, or expires at `end_time`."""

  stop_limit_stop_limit_gtd: (
    StopLimitStopLimitGtdAttachedOrderConfigurationAnyOf8StopLimitStopLimitGtd
  )


class StopLimitStopLimitGtdConfigurationOrderConfigurationAnyOf8(TypedDict):
  """Stop-limit order, good-till-date: becomes a limit order once the last trade price crosses `stop_price`, or expires at `end_time`."""

  stop_limit_stop_limit_gtd: (
    StopLimitStopLimitGtdOrderConfigurationAnyOf8StopLimitStopLimitGtd
  )


class TriggerBracketGtcConfigurationAttachedOrderConfigurationAnyOf9(TypedDict):
  """Bracket order, good-till-cancelled: a limit order with an embedded take-profit/stop-loss exit at `stop_trigger_price`."""

  trigger_bracket_gtc: (
    TriggerBracketGtcAttachedOrderConfigurationAnyOf9TriggerBracketGtc
  )


class TriggerBracketGtcConfigurationOrderConfigurationAnyOf9(TypedDict):
  """Bracket order, good-till-cancelled: a limit order with an embedded take-profit/stop-loss exit at `stop_trigger_price`."""

  trigger_bracket_gtc: TriggerBracketGtcOrderConfigurationAnyOf9TriggerBracketGtc


class TriggerBracketGtdConfigurationAttachedOrderConfigurationAnyOf10(TypedDict):
  """Bracket order, good-till-date: a limit order with an embedded take-profit/stop-loss exit at `stop_trigger_price`, expiring at `end_time`."""

  trigger_bracket_gtd: (
    TriggerBracketGtdAttachedOrderConfigurationAnyOf10TriggerBracketGtd
  )


class TriggerBracketGtdConfigurationOrderConfigurationAnyOf10(TypedDict):
  """Bracket order, good-till-date: a limit order with an embedded take-profit/stop-loss exit at `stop_trigger_price`, expiring at `end_time`."""

  trigger_bracket_gtd: TriggerBracketGtdOrderConfigurationAnyOf10TriggerBracketGtd


class TwapLimitGtdConfigurationAttachedOrderConfigurationAnyOf6(TypedDict):
  """Time-weighted-average-price order: splits execution into equal-sized limit suborders spread across a time window."""

  twap_limit_gtd: TwapLimitGtdAttachedOrderConfigurationAnyOf6TwapLimitGtd


class TwapLimitGtdConfigurationOrderConfigurationAnyOf6(TypedDict):
  """Time-weighted-average-price order: splits execution into equal-sized limit suborders spread across a time window."""

  twap_limit_gtd: TwapLimitGtdOrderConfigurationAnyOf6TwapLimitGtd


class LimitLimitGtcConfigurationAttachedOrderConfigurationAnyOf3(TypedDict):
  """Limit order, good-till-cancelled: remains on the order book until filled or cancelled."""

  limit_limit_gtc: LimitLimitGtcAttachedOrderConfigurationAnyOf3LimitLimitGtc


class LimitLimitGtcConfigurationOrderConfigurationAnyOf3(TypedDict):
  """Limit order, good-till-cancelled: remains on the order book until filled or cancelled."""

  limit_limit_gtc: LimitLimitGtcOrderConfigurationAnyOf3LimitLimitGtc


class LimitLimitGtdConfigurationAttachedOrderConfigurationAnyOf4(TypedDict):
  """Limit order, good-till-date: remains on the order book until filled, cancelled, or `end_time`."""

  limit_limit_gtd: LimitLimitGtdAttachedOrderConfigurationAnyOf4LimitLimitGtd


class LimitLimitGtdConfigurationOrderConfigurationAnyOf4(TypedDict):
  """Limit order, good-till-date: remains on the order book until filled, cancelled, or `end_time`."""

  limit_limit_gtd: LimitLimitGtdOrderConfigurationAnyOf4LimitLimitGtd


class MarketMarketIocConfigurationAttachedOrderConfigurationAnyOf0(TypedDict):
  """Market order, immediate-or-cancel: fills at the current best available price, any unfilled remainder is cancelled."""

  market_market_ioc: MarketMarketIocAttachedOrderConfigurationAnyOf0MarketMarketIoc


class MarketMarketIocConfigurationOrderConfigurationAnyOf0(TypedDict):
  """Market order, immediate-or-cancel: fills at the current best available price, any unfilled remainder is cancelled."""

  market_market_ioc: MarketMarketIocOrderConfigurationAnyOf0MarketMarketIoc


class ScaledLimitGtcConfigurationAttachedOrderConfigurationAnyOf11(TypedDict):
  """Scaled order, good-till-cancelled: a ladder of limit child orders spread across a price range."""

  scaled_limit_gtc: ScaledLimitGtcAttachedOrderConfigurationAnyOf11ScaledLimitGtc


class ScaledLimitGtcConfigurationOrderConfigurationAnyOf11(TypedDict):
  """Scaled order, good-till-cancelled: a ladder of limit child orders spread across a price range."""

  scaled_limit_gtc: ScaledLimitGtcOrderConfigurationAnyOf11ScaledLimitGtc


class Order(TypedDict):
  """A single Advanced Trade order."""

  order_id: str
  """The order's unique id."""
  product_id: str
  """Trading pair, e.g. `BTC-USD`."""
  user_id: str
  """Id of the user owning the order."""
  side: Literal['BUY', 'SELL']
  """Trade direction."""
  order_configuration: (
    MarketMarketIocConfigurationOrderConfigurationAnyOf0
    | MarketMarketFokConfigurationOrderConfigurationAnyOf1
    | SorLimitIocConfigurationOrderConfigurationAnyOf2
    | LimitLimitGtcConfigurationOrderConfigurationAnyOf3
    | LimitLimitGtdConfigurationOrderConfigurationAnyOf4
    | LimitLimitFokConfigurationOrderConfigurationAnyOf5
    | TwapLimitGtdConfigurationOrderConfigurationAnyOf6
    | StopLimitStopLimitGtcConfigurationOrderConfigurationAnyOf7
    | StopLimitStopLimitGtdConfigurationOrderConfigurationAnyOf8
    | TriggerBracketGtcConfigurationOrderConfigurationAnyOf9
    | TriggerBracketGtdConfigurationOrderConfigurationAnyOf10
    | ScaledLimitGtcConfigurationOrderConfigurationAnyOf11
  )
  """Order type, size, and pricing."""
  status: Literal[
    'PENDING',
    'OPEN',
    'FILLED',
    'CANCELLED',
    'EXPIRED',
    'FAILED',
    'UNKNOWN_ORDER_STATUS',
    'QUEUED',
    'CANCEL_QUEUED',
    'EDIT_QUEUED',
  ]
  """Current lifecycle state."""
  client_order_id: str
  """Client-provided identifier, unique per order."""
  created_time: str
  """RFC3339 order creation time."""
  completion_percentage: str
  """Percent of the order filled, e.g. `"50"`."""
  average_filled_price: str
  """Average price across all fills."""
  number_of_fills: str
  """Count of fill records posted for this order."""
  filled_size: NotRequired[str]
  """Portion filled, in base currency."""
  filled_value: NotRequired[str]
  """Portion filled, in quote currency."""
  time_in_force: NotRequired[
    Literal[
      'UNKNOWN_TIME_IN_FORCE',
      'GOOD_UNTIL_DATE_TIME',
      'GOOD_UNTIL_CANCELLED',
      'IMMEDIATE_OR_CANCEL',
      'FILL_OR_KILL',
    ]
  ]
  """Window of order validity."""
  fee: NotRequired[str]
  """Deprecated commission amount."""
  total_fees: str
  """Total fees charged on the order."""
  pending_cancel: bool
  """A cancel request was initiated but hasn't completed."""
  size_in_quote: bool
  """Whether the order was sized in quote currency."""
  size_inclusive_of_fees: bool
  """Whether `filled_size`/`filled_value` include fees."""
  total_value_after_fees: str
  """`filled_value` plus or minus `total_fees`."""
  trigger_status: NotRequired[
    Literal[
      'UNKNOWN_TRIGGER_STATUS', 'INVALID_ORDER_TYPE', 'STOP_PENDING', 'STOP_TRIGGERED'
    ]
  ]
  """Trigger state, for stop orders."""
  order_type: NotRequired[
    Literal[
      'UNKNOWN_ORDER_TYPE',
      'MARKET',
      'LIMIT',
      'STOP',
      'STOP_LIMIT',
      'BRACKET',
      'TWAP',
      'ROLL_OPEN',
      'ROLL_CLOSE',
      'LIQUIDATION',
      'SCALED',
    ]
  ]
  """Order classification."""
  reject_reason: NotRequired[
    Literal[
      'REJECT_REASON_UNSPECIFIED',
      'HOLD_FAILURE',
      'TOO_MANY_OPEN_ORDERS',
      'REJECT_REASON_INSUFFICIENT_FUNDS',
      'RATE_LIMIT_EXCEEDED',
    ]
  ]
  """Why the order was rejected, when applicable."""
  reject_message: NotRequired[str]
  """Human-readable rejection explanation."""
  settled: NotRequired[bool]
  """Whether the order is fully filled and settled."""
  product_type: NotRequired[
    Literal[
      'UNKNOWN_PRODUCT_TYPE', 'SPOT', 'FUTURE', 'EQUITY', 'OPTION_GROUP', 'FUTURE_GROUP'
    ]
  ]
  """Class of the traded product."""
  cancel_message: NotRequired[str]
  """Human-readable cancellation explanation."""
  order_placement_source: NotRequired[
    Literal[
      'UNKNOWN_PLACEMENT_SOURCE',
      'RETAIL_SIMPLE',
      'RETAIL_ADVANCED',
      'RETAIL_ADMIN',
      'RETAIL_RAISE',
    ]
  ]
  """Which surface placed the order."""
  outstanding_hold_amount: NotRequired[str]
  """Remaining balance hold for this order."""
  is_liquidation: NotRequired[bool]
  """Whether this is a liquidation order."""
  last_fill_time: NotRequired[str | None]
  """RFC3339 time of the most recent fill."""
  edit_history: NotRequired[list[EditItem]]
  """Up to the last 5 edits applied to this order."""
  leverage: NotRequired[str]
  """Leverage applied to the order; defaults to `"1.0"`."""
  margin_type: NotRequired[Literal['CROSS', 'ISOLATED', 'UNKNOWN_MARGIN_TYPE']]
  """Cross or isolated margin."""
  retail_portfolio_id: NotRequired[str]
  """Deprecated portfolio association; legacy keys only."""
  originating_order_id: NotRequired[str]
  """Parent order id, for an attached order."""
  attached_order_id: NotRequired[str]
  """Attached order id, for a parent order."""
  attached_order_configuration: NotRequired[
    MarketMarketIocConfigurationAttachedOrderConfigurationAnyOf0
    | MarketMarketFokConfigurationAttachedOrderConfigurationAnyOf1
    | SorLimitIocConfigurationAttachedOrderConfigurationAnyOf2
    | LimitLimitGtcConfigurationAttachedOrderConfigurationAnyOf3
    | LimitLimitGtdConfigurationAttachedOrderConfigurationAnyOf4
    | LimitLimitFokConfigurationAttachedOrderConfigurationAnyOf5
    | TwapLimitGtdConfigurationAttachedOrderConfigurationAnyOf6
    | StopLimitStopLimitGtcConfigurationAttachedOrderConfigurationAnyOf7
    | StopLimitStopLimitGtdConfigurationAttachedOrderConfigurationAnyOf8
    | TriggerBracketGtcConfigurationAttachedOrderConfigurationAnyOf9
    | TriggerBracketGtdConfigurationAttachedOrderConfigurationAnyOf10
    | ScaledLimitGtcConfigurationAttachedOrderConfigurationAnyOf11
    | None
  ]
  """Configuration of the attached (bracket) order."""
  current_pending_replace: NotRequired[Edit0 | None]
  """Price/size of an edit currently in flight."""
  commission_detail_total: NotRequired[CommissionDetailTotal]
  workable_size: NotRequired[str]
  """Filled portion of the originating order, for an attached order."""
  workable_size_completion_pct: NotRequired[str]
  """Percentage of the originating order filled."""
  product_details: NotRequired[ProductDetails | None]
  """Product-type-specific details."""
  cost_basis_method: NotRequired[
    Literal[
      'COST_BASIS_METHOD_UNSPECIFIED',
      'COST_BASIS_METHOD_HIFO',
      'COST_BASIS_METHOD_LIFO',
      'COST_BASIS_METHOD_FIFO',
      'COST_BASIS_METHOD_SPEC_ID',
    ]
  ]
  """Tax lot matching method."""
  displayed_order_config: NotRequired[
    Literal[
      'UNKNOWN_DISPLAYED_ORDER_CONFIG',
      'INSTANT_GFD',
      'LIMIT_GFD',
      'LIMIT_GTC',
      'MARKET_GFD',
      'EXERCISE_GFD',
    ]
  ]
  """Equity time-in-force display encoding."""
  equity_trading_session: NotRequired[
    Literal[
      'UNKNOWN_EQUITY_TRADING_SESSION',
      'EQUITY_TRADING_SESSION_NORMAL',
      'EQUITY_TRADING_SESSION_AFTER_HOURS',
      'EQUITY_TRADING_SESSION_MULTI_SESSION',
      'EQUITY_TRADING_SESSION_OVERNIGHT',
      'EQUITY_TRADING_SESSION_PRE_MARKET',
    ]
  ]
  """Equity market session the order executes in."""
  prediction_side: NotRequired[
    Literal['PREDICTION_SIDE_UNKNOWN', 'PREDICTION_SIDE_YES', 'PREDICTION_SIDE_NO']
  ]
  """Side of a prediction-market order."""
  last_update_time: NotRequired[str]
  """RFC3339 time of the most recent update to this order (most recent fill time, else creation time)."""
  total_value_after_fees_native: NotRequired[
    AmountTotalValueAfterFeesNativeAnyOf0 | None
  ]
  """`total_value_after_fees` converted to the account's native currency. Empty when rates are unavailable."""
  outstanding_hold_amount_native: NotRequired[
    AmountOutstandingHoldAmountNativeAnyOf0 | None
  ]
  """`outstanding_hold_amount` converted to the account's native currency (source currency is quote for BUY, base for SELL). Empty when rates are unavailable."""
  total_fees_native: NotRequired[AmountTotalFeesNativeAnyOf0 | None]
  """`total_fees` converted to the account's native currency. Empty when rates are unavailable."""


class ListOrdersResponse(TypedDict):
  orders: list[Order]
  """Matching orders, newest first."""
  has_next: bool
  """Whether another page is available."""
  cursor: NotRequired[str]
  """Cursor for the next page, when `has_next` is true."""
  sequence: NotRequired[str]
  """Deprecated sequence number."""
  proof_token_required: NotRequired[bool]
  """Whether a `proof_token` is required to complete this request, for EU Strong Customer Authentication."""


@dataclass(frozen=True, kw_only=True)
class Batch(RpcEndpoint):
  """`GET /api/v3/brokerage/orders/historical/batch`."""

  async def batch(
    self,
    *,
    order_ids: list[str] | None = None,
    product_ids: list[str] | None = None,
    product_type: Literal[
      'UNKNOWN_PRODUCT_TYPE', 'SPOT', 'FUTURE', 'EQUITY', 'OPTION_GROUP', 'FUTURE_GROUP'
    ]
    | None = None,
    order_status: list[
      Literal[
        'PENDING',
        'OPEN',
        'FILLED',
        'CANCELLED',
        'EXPIRED',
        'FAILED',
        'UNKNOWN_ORDER_STATUS',
        'QUEUED',
        'CANCEL_QUEUED',
        'EDIT_QUEUED',
      ]
    ]
    | None = None,
    time_in_forces: list[
      Literal[
        'UNKNOWN_TIME_IN_FORCE',
        'GOOD_UNTIL_DATE_TIME',
        'GOOD_UNTIL_CANCELLED',
        'IMMEDIATE_OR_CANCEL',
        'FILL_OR_KILL',
      ]
    ]
    | None = None,
    order_types: list[
      Literal[
        'UNKNOWN_ORDER_TYPE',
        'MARKET',
        'LIMIT',
        'STOP',
        'STOP_LIMIT',
        'BRACKET',
        'TWAP',
        'ROLL_OPEN',
        'ROLL_CLOSE',
        'LIQUIDATION',
        'SCALED',
      ]
    ]
    | None = None,
    order_side: Literal['BUY', 'SELL'] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    order_placement_source: Literal[
      'UNKNOWN_PLACEMENT_SOURCE',
      'RETAIL_SIMPLE',
      'RETAIL_ADVANCED',
      'RETAIL_ADMIN',
      'RETAIL_RAISE',
    ]
    | None = None,
    contract_expiry_type: Literal[
      'UNKNOWN_CONTRACT_EXPIRY_TYPE', 'EXPIRING', 'PERPETUAL'
    ]
    | None = None,
    asset_filters: list[str] | None = None,
    retail_portfolio_id: str | None = None,
    limit: int | None = None,
    cursor: str | None = None,
    sort_by: Literal[
      'UNKNOWN_SORT_BY', 'LIMIT_PRICE', 'LAST_FILL_TIME', 'LAST_UPDATE_TIME'
    ]
    | None = None,
    use_simplified_total_value_calculation: bool | None = None,
    proof_token: str | None = None,
  ) -> ListOrdersResponse:
    """List historical orders, newest first, optionally filtered by id/product/status/type/side/date range. Set `product_type` to `EQUITY` to return only equity orders.

    Args:
      order_ids: Only return orders with these ids.
      product_ids: Only return orders for these product ids. For equities, use the canonical product id, not the display ticker.
      product_type: Only return orders for this product type; defaults to all types.
      order_status: Only return orders in these statuses.
      time_in_forces: Only return orders with these time-in-force types; defaults to all.
      order_types: Only return orders of these types; defaults to all.
      order_side: Only return orders on this side; both sides are returned by default.
      start_date: Inclusive lower bound on order creation time.
      end_date: Exclusive upper bound on order creation time.
      order_placement_source: Only return orders placed from this source; defaults to `RETAIL_ADVANCED`.
      contract_expiry_type: Only return futures orders of this expiry type; only applicable when `product_type` is `FUTURE`.
      asset_filters: Only return orders touching one of these assets (quote, base, or underlying), e.g. `["BTC"]`.
      retail_portfolio_id: Deprecated. Only orders matching this retail portfolio id are returned; legacy keys only. CDP keys default to the key's permissioned portfolio.
      limit: Page size. No default; if `has_next` is true, more pages are available.
      cursor: Cursor from a previous page's `cursor` field.
      sort_by: Field to sort results by; sorting by anything other than creation time uses unstable pagination. Defaults to sort by creation time.
      use_simplified_total_value_calculation: Use a simplified total-value calculation; defaults to true.
      proof_token: Optional two-factor validation token, for EU Strong Customer Authentication.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/orders/list-orders)
    """
    params = {}
    if order_ids is not None:
      params['order_ids'] = order_ids
    if product_ids is not None:
      params['product_ids'] = product_ids
    if product_type is not None:
      params['product_type'] = product_type
    if order_status is not None:
      params['order_status'] = order_status
    if time_in_forces is not None:
      params['time_in_forces'] = time_in_forces
    if order_types is not None:
      params['order_types'] = order_types
    if order_side is not None:
      params['order_side'] = order_side
    if start_date is not None:
      params['start_date'] = start_date
    if end_date is not None:
      params['end_date'] = end_date
    if order_placement_source is not None:
      params['order_placement_source'] = order_placement_source
    if contract_expiry_type is not None:
      params['contract_expiry_type'] = contract_expiry_type
    if asset_filters is not None:
      params['asset_filters'] = asset_filters
    if retail_portfolio_id is not None:
      params['retail_portfolio_id'] = retail_portfolio_id
    if limit is not None:
      params['limit'] = limit
    if cursor is not None:
      params['cursor'] = cursor
    if sort_by is not None:
      params['sort_by'] = sort_by
    if use_simplified_total_value_calculation is not None:
      params['use_simplified_total_value_calculation'] = (
        use_simplified_total_value_calculation
      )
    if proof_token is not None:
      params['proof_token'] = proof_token
    return await self.authed_request(
      'GET',
      '/api/v3/brokerage/orders/historical/batch',
      params=params,
      validator=validator(ListOrdersResponse),
    )

  async def batch_paged(
    self,
    *,
    order_ids: list[str] | None = None,
    product_ids: list[str] | None = None,
    product_type: Literal[
      'UNKNOWN_PRODUCT_TYPE', 'SPOT', 'FUTURE', 'EQUITY', 'OPTION_GROUP', 'FUTURE_GROUP'
    ]
    | None = None,
    order_status: list[
      Literal[
        'PENDING',
        'OPEN',
        'FILLED',
        'CANCELLED',
        'EXPIRED',
        'FAILED',
        'UNKNOWN_ORDER_STATUS',
        'QUEUED',
        'CANCEL_QUEUED',
        'EDIT_QUEUED',
      ]
    ]
    | None = None,
    time_in_forces: list[
      Literal[
        'UNKNOWN_TIME_IN_FORCE',
        'GOOD_UNTIL_DATE_TIME',
        'GOOD_UNTIL_CANCELLED',
        'IMMEDIATE_OR_CANCEL',
        'FILL_OR_KILL',
      ]
    ]
    | None = None,
    order_types: list[
      Literal[
        'UNKNOWN_ORDER_TYPE',
        'MARKET',
        'LIMIT',
        'STOP',
        'STOP_LIMIT',
        'BRACKET',
        'TWAP',
        'ROLL_OPEN',
        'ROLL_CLOSE',
        'LIQUIDATION',
        'SCALED',
      ]
    ]
    | None = None,
    order_side: Literal['BUY', 'SELL'] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    order_placement_source: Literal[
      'UNKNOWN_PLACEMENT_SOURCE',
      'RETAIL_SIMPLE',
      'RETAIL_ADVANCED',
      'RETAIL_ADMIN',
      'RETAIL_RAISE',
    ]
    | None = None,
    contract_expiry_type: Literal[
      'UNKNOWN_CONTRACT_EXPIRY_TYPE', 'EXPIRING', 'PERPETUAL'
    ]
    | None = None,
    asset_filters: list[str] | None = None,
    retail_portfolio_id: str | None = None,
    limit: int | None = None,
    sort_by: Literal[
      'UNKNOWN_SORT_BY', 'LIMIT_PRICE', 'LAST_FILL_TIME', 'LAST_UPDATE_TIME'
    ]
    | None = None,
    use_simplified_total_value_calculation: bool | None = None,
    proof_token: str | None = None,
    max_pages: int | None = None,
  ) -> AsyncIterator[ListOrdersResponse]:
    """Yield successive pages of `batch`.

    Passes each page's token back as `cursor` and stops when a response carries no
    `cursor`, or after `max_pages` pages when one is given.
    """
    cursor: str | None = None
    pages = 0
    while True:
      response = await self.batch(
        order_ids=order_ids,
        product_ids=product_ids,
        product_type=product_type,
        order_status=order_status,
        time_in_forces=time_in_forces,
        order_types=order_types,
        order_side=order_side,
        start_date=start_date,
        end_date=end_date,
        order_placement_source=order_placement_source,
        contract_expiry_type=contract_expiry_type,
        asset_filters=asset_filters,
        retail_portfolio_id=retail_portfolio_id,
        limit=limit,
        sort_by=sort_by,
        use_simplified_total_value_calculation=use_simplified_total_value_calculation,
        proof_token=proof_token,
        cursor=cursor,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      cursor = response.get('cursor') if response is not None else None
      if not cursor:
        break
