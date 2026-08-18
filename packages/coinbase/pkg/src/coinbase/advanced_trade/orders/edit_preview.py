from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class Amount(TypedDict):
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""

  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class CommissionDetailTotal(TypedDict):
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


class EditOrderPreviewError(TypedDict):
  edit_failure_reason: NotRequired[
    Literal[
      'UNKNOWN_EDIT_ORDER_FAILURE_REASON',
      'COMMANDER_REJECTED_EDIT_ORDER',
      'CANNOT_EDIT_TO_BELOW_FILLED_SIZE',
      'ORDER_NOT_FOUND',
      'CALLER_ID_MISMATCH',
      'ONLY_LIMIT_ORDER_EDITS_SUPPORTED',
      'INVALID_EDITED_SIZE',
      'INVALID_EDITED_PRICE',
      'INVALID_ORIGINAL_SIZE',
      'INVALID_ORIGINAL_PRICE',
      'EDIT_REQUEST_EQUAL_TO_ORIGINAL_REQUEST',
      'ONLY_OPEN_ORDERS_CAN_BE_EDITED',
      'SIZE_IN_QUOTE_EDITS_NOT_ALLOWED',
      'ORDER_IS_ALREADY_BEING_REPLACED',
      'PORTFOLIO_NOT_ALLOWED_FOR_EDITS',
      'STRATEGY_NOT_SUPPORTED',
      'FIELD_STOPPRICE_NOT_SUPPORTED',
      'FIELD_DISPLAYSIZE_NOT_SUPPORTED',
      'FIELD_ENDTIME_NOT_SUPPORTED',
      'INVALID_ORIGINAL_TIME',
      'INVALID_NEW_ENDTIME',
      'NOT_STARTED',
      'CANNOT_EDIT_FUTURES_ORDER',
      'FUTURES_VENUE_ORDER_NOT_FOUND',
      'CANNOT_EDIT_STOP_PRICE_FOR_TRIGGERED_ORDER',
      'CANNOT_EDIT_ORDER_PENDING_CANCEL',
      'INSUFFICIENT_TIME_TO_EDIT',
      'EXCEEDED_MAX_ALLOWED_EDIT_REQUEST_COUNT',
      'CANNOT_CANCEL_ACTIVE_ATTACHED_ORDER',
      'ORDER_EDIT_INVALID_ATTACHED_ORDER_REQUEST',
      'ORDER_EDIT_ORDER_TYPE_NOT_SUPPORTED',
      'CANNOT_EDIT_TRIGGERED_ORDER',
      'INVALID_EDITED_STOP_PRICE',
      'INVALID_EDITED_STOP_LIMIT_PRICE',
      'INVALID_ORIGINAL_STOP_PRICE',
      'INVALID_ORIGINAL_STOP_LIMIT_PRICE',
      'INVALID_ORIGINAL_ATTACHED_ORDER_CONFIG',
      'CANNOT_EDIT_ATTACHED_ORDER_CONFIGURATION_AFTER_CREATION',
      'CANNOT_CONVERT_SIZE_ASSET',
      'CANNOT_CONVERT_DISPLAY_SIZE_ASSET',
      'CANNOT_EDIT_ATTACHED_ORDER_SIZE_WITH_OPEN_ORIGINATING_ORDER',
      'INVALID_EDITED_TAKE_PROFIT_PRICE',
      'INVALID_EDITED_STOP_LOSS_PRICE',
      'INVALID_EDITED_ATTACHED_ORDER_CONFIGURATION',
      'CANNOT_EDIT_ATTACHED_SL_ORDER_PRICE',
      'CANNOT_ADD_ATTACHED_ORDER_TO_ORDER_TYPE',
      'CANNOT_CHANGE_SIDE_OF_ORDER',
      'CANNOT_CHANGE_ORDER_TYPE_OF_ORDER',
      'CANNOT_CHANGE_PRODUCT_ID_OF_ORDER',
      'PREV_CLIENT_ORDER_ID_REQUIRED_WHEN_CLIENT_ORDER_ID_PROVIDED',
      'CLIENT_ORDER_ID_REQUIRED_WHEN_PREV_CLIENT_ORDER_ID_PROVIDED',
      'CLIENT_ORDER_ID_MUST_BE_DIFFERENT_FROM_PREV_CLIENT_ORDER_ID',
      'PREV_CLIENT_ORDER_ID_MUST_MATCH_CURRENT_CLIENT_ORDER_ID',
      'CANNOT_MODIFY_ATTACHED_CONFIG_OF_NON_NEW_ORDER',
      'INVALID_EDITED_ATTACHED_ORDER_CONFIGURATION_NON_MODIFIABLE_VALUE_EDIT',
      'ATTACHED_CONFIGURATION_IS_EQUAL',
      'CANNOT_ADD_LEG_TO_TPSL_ORDER',
      'CANNOT_REMOVE_LEG_FROM_TPSL_ORDER',
      'SINGLE_LEGGED_BRACKET_ORDER_NOT_ALLOWED',
      'SINGLE_LEGGED_ATTACHED_ORDER_CONFIGURATION_NOT_ALLOWED',
      'FIELD_PEG_OFFSET_NOT_SUPPORTED',
      'INVALID_EDITED_PEG_WIG_LEVEL',
      'INVALID_EDITED_PEG_OFFSET',
      'FIELD_PEG_WIG_LEVEL_NOT_SUPPORTED',
    ]
  ]
  """Machine-readable edit failure code."""
  preview_failure_reason: NotRequired[
    Literal[
      'UNKNOWN_PREVIEW_FAILURE_REASON',
      'PREVIEW_MISSING_COMMISSION_RATE',
      'PREVIEW_INVALID_SIDE',
      'PREVIEW_INVALID_ORDER_CONFIG',
      'PREVIEW_INVALID_PRODUCT_ID',
      'PREVIEW_INVALID_SIZE_PRECISION',
      'PREVIEW_INVALID_PRICE_PRECISION',
      'PREVIEW_MISSING_PRODUCT_PRICE_BOOK',
      'PREVIEW_INVALID_LEDGER_BALANCE',
      'PREVIEW_INSUFFICIENT_LEDGER_BALANCE',
      'PREVIEW_INVALID_LIMIT_PRICE_POST_ONLY',
      'PREVIEW_INVALID_LIMIT_PRICE',
      'PREVIEW_INVALID_NO_LIQUIDITY',
      'PREVIEW_INSUFFICIENT_FUND',
      'PREVIEW_INVALID_COMMISSION_CONFIGURATION',
      'PREVIEW_INVALID_STOP_PRICE',
      'PREVIEW_INVALID_BASE_SIZE_TOO_LARGE',
      'PREVIEW_INVALID_BASE_SIZE_TOO_SMALL',
      'PREVIEW_INVALID_QUOTE_SIZE_PRECISION',
      'PREVIEW_INVALID_QUOTE_SIZE_TOO_LARGE',
      'PREVIEW_INVALID_PRICE_TOO_LARGE',
      'PREVIEW_INVALID_QUOTE_SIZE_TOO_SMALL',
      'PREVIEW_INSUFFICIENT_FUNDS_FOR_FUTURES',
      'PREVIEW_BREACHED_PRICE_LIMIT',
      'PREVIEW_BREACHED_ACCOUNT_POSITION_LIMIT',
      'PREVIEW_BREACHED_COMPANY_POSITION_LIMIT',
      'PREVIEW_INVALID_MARGIN_HEALTH',
      'PREVIEW_RISK_PROXY_FAILURE',
      'PREVIEW_UNTRADABLE_FCM_ACCOUNT_STATUS',
      'PREVIEW_IN_LIQUIDATION',
      'PREVIEW_INVALID_MARGIN_TYPE',
      'PREVIEW_INVALID_LEVERAGE',
      'PREVIEW_UNTRADABLE_PRODUCT',
      'PREVIEW_INVALID_FCM_TRADING_SESSION',
      'PREVIEW_NOT_ALLOWED_BY_MARKET_STATE',
      'PREVIEW_BREACHED_OPEN_INTEREST_LIMIT',
      'PREVIEW_GEOFENCING_RESTRICTION',
      'PREVIEW_INVALID_END_TIME',
      'PREVIEW_OPPOSITE_MARGIN_TYPE_EXISTS',
      'PREVIEW_QUOTE_SIZE_NOT_ALLOWED_FOR_BRACKET',
      'PREVIEW_INVALID_BRACKET_PRICES',
      'PREVIEW_MISSING_MARKET_TRADE_DATA',
      'PREVIEW_INVALID_BRACKET_LIMIT_PRICE',
      'PREVIEW_INVALID_BRACKET_STOP_TRIGGER_PRICE',
      'PREVIEW_BRACKET_LIMIT_PRICE_OUT_OF_BOUNDS',
      'PREVIEW_STOP_TRIGGER_PRICE_OUT_OF_BOUNDS',
      'PREVIEW_BRACKET_ORDER_NOT_SUPPORTED',
      'PREVIEW_INVALID_STOP_PRICE_PRECISION',
      'PREVIEW_STOP_PRICE_ABOVE_LIMIT_PRICE',
      'PREVIEW_STOP_PRICE_BELOW_LIMIT_PRICE',
      'PREVIEW_STOP_PRICE_ABOVE_LAST_TRADE_PRICE',
      'PREVIEW_STOP_PRICE_BELOW_LAST_TRADE_PRICE',
      'PREVIEW_FOK_DISABLED',
      'PREVIEW_FOK_ONLY_ALLOWED_ON_LIMIT_ORDERS',
      'PREVIEW_POST_ONLY_NOT_ALLOWED_WITH_FOK',
      'PREVIEW_UBO_HIGH_LEVERAGE_QUANTITY_BREACHED',
      'PREVIEW_ECOSYSTEM_LEVERAGE_UTILIZATION_BREACHED',
      'PREVIEW_CLOSE_ONLY_FAILURE',
      'PREVIEW_UBO_HIGH_LEVERAGE_NOTIONAL_BREACHED',
      'PREVIEW_END_TIME_TOO_FAR_IN_FUTURE',
      'PREVIEW_LIMIT_PRICE_TOO_FAR_FROM_MARKET',
      'PREVIEW_FUTURES_AFTER_HOUR_INVALID_ORDER_TYPE',
      'PREVIEW_FUTURES_AFTER_HOUR_INVALID_TIME_IN_FORCE',
      'PREVIEW_INVALID_ATTACHED_TAKE_PROFIT_PRICE',
      'PREVIEW_INVALID_ATTACHED_STOP_LOSS_PRICE',
      'PREVIEW_INVALID_ATTACHED_TAKE_PROFIT_PRICE_PRECISION',
      'PREVIEW_INVALID_ATTACHED_STOP_LOSS_PRICE_PRECISION',
      'PREVIEW_INVALID_ATTACHED_TAKE_PROFIT_PRICE_OUT_OF_BOUNDS',
      'PREVIEW_INVALID_ATTACHED_STOP_LOSS_PRICE_OUT_OF_BOUNDS',
      'PREVIEW_INVALID_BRACKET_ORDER_SIDE',
      'PREVIEW_BRACKET_ORDER_SIZE_EXCEEDS_POSITION',
      'PREVIEW_ORDER_SIZE_EXCEEDS_BRACKETED_POSITION',
      'PREVIEW_INVALID_LIMIT_PRICE_PRECISION',
      'PREVIEW_INVALID_STOP_TRIGGER_PRICE_PRECISION',
      'PREVIEW_INVALID_ATTACHED_TAKE_PROFIT_PRICE_EXCEEDS_MAX_DISTANCE_FROM_ORIGINATING_PRICE',
      'PREVIEW_INVALID_ATTACHED_TAKE_PROFIT_SIZE_BELOW_MIN',
      'PREVIEW_ATTACHED_ORDER_SIZE_MUST_BE_NIL',
      'PREVIEW_BELOW_MIN_SIZE_FOR_DURATION',
      'PREVIEW_MAX_DAILY_VOLUME_NOTIONAL_BREACHED',
      'PREVIEW_INVALID_SETTLEMENT_CURRENCY',
      'PREVIEW_DURATION_TOO_SMALL',
      'PREVIEW_INTX_FOK_ONLY_ALLOWED_ON_LIMIT_AND_MARKET_ORDERS',
      'PREVIEW_BUCKET_SIZE_SMALLER_THAN_QUOTE_MIN',
      'PREVIEW_BUCKET_SIZE_SMALLER_THAN_BASE_MIN',
      'PREVIEW_END_TIME_AFTER_CONTRACT_EXPIRATION',
      'PREVIEW_START_TIME_MUST_BE_SPECIFIED',
      'PREVIEW_ICEBERG_ORDERS_NOT_SUPPORTED',
      'PREVIEW_END_TIME_IS_IN_THE_PAST',
      'PREVIEW_GTD_ORDERS_MUST_HAVE_END_TIME',
      'PREVIEW_ATTACHED_ORDER_MUST_HAVE_POSITIVE_PRICES',
      'PREVIEW_INVALID_ORDER_SIDE_FOR_ATTACHED_TPSL',
      'PREVIEW_ATTACHED_ORDERS_ONLY_ALLOWED_ON_MARKET_LIMIT',
      'PREVIEW_INVALID_ORDER_TYPE_FOR_ATTACHED',
      'PREVIEW_PRICE_NOT_ALLOWED_FOR_MARKET_ORDERS',
      'PREVIEW_REDUCE_ONLY_NOT_ALLOWED_ON_VENUE',
      'PREVIEW_NON_NUMERIC_ORDER_SIZE',
      'PREVIEW_INVALID_INTX_CLIENT_ORDER_ID',
      'PREVIEW_DURATION_TOO_LARGE',
      'PREVIEW_REDUCE_ONLY_NOT_ALLOWED_ON_SPOT_PRODUCTS',
      'PREVIEW_LIMIT_ORDER_PRICE_EXCEEDS_PRICE_BAND_ON_BUY',
      'PREVIEW_LIMIT_ORDER_PRICE_EXCEEDS_PRICE_BAND_ON_SELL',
      'PREVIEW_INVALID_ATTACHED_TAKE_PROFIT_PRICE_OUT_OF_BOUNDS_ON_AGGRESSIVE_ORDER',
      'PREVIEW_INVALID_ATTACHED_STOP_LOSS_PRICE_OUT_OF_BOUNDS_ON_AGGRESSIVE_ORDER',
      'PREVIEW_STOP_TRIGGERED',
      'PREVIEW_REPLACE_NOT_SUPPORTED',
      'PREVIEW_ORDER_IS_PENDING_CANCEL',
      'PREVIEW_POSITION_SIZE_INCREASE_REJECT',
      'PREVIEW_ASSET_BALANCE_INCREASE_REJECT',
      'PREVIEW_TOO_MANY_PENDING_REPLACES',
      'PREVIEW_INVALID_RFQ_BASE_SIZE_TOO_SMALL',
      'PREVIEW_INVALID_RFQ_BASE_SIZE_TOO_LARGE',
      'PREVIEW_INVALID_RFQ_QUOTE_SIZE_TOO_SMALL',
      'PREVIEW_INVALID_RFQ_QUOTE_SIZE_TOO_LARGE',
      'PREVIEW_REDUCE_ONLY_INCREASED_POSITION_SIZE',
      'PREVIEW_COMPLIANCE_PURCHASE_LIMIT_EXCEEDED',
      'PREVIEW_SCALED_PARAM_INFEASIBLE',
      'PREVIEW_SCALED_MIN_ORDER_VIOLATION',
      'PREVIEW_SCALED_MAX_ORDER_VIOLATION',
      'PREVIEW_POST_ONLY_NOT_ALLOWED_WITH_PEG',
      'PREVIEW_INVALID_PEG_OFFSET',
      'PREVIEW_INVALID_PEG_WIG_LEVEL',
      'PREVIEW_INVALID_PEG_VENUE_OPTIONS',
      'PREVIEW_PEG_INVALID_ORDER_TYPE',
      'PREVIEW_SINGLE_LEGGED_TPSL_NOT_ALLOWED',
      'PREVIEW_FRACTIONAL_ORDERS_NOT_ALLOWED_FOR_PRODUCT',
      'PREVIEW_QUOTE_ORDERS_NOT_ALLOWED_FOR_PRODUCT',
      'PREVIEW_NBBO_NOT_PROVIDED',
      'PREVIEW_INVALID_NBBO_BID_PRICE',
      'PREVIEW_INVALID_NBBO_ASK_PRICE',
      'PREVIEW_NOTIONAL_SIZE_BREACHES_FRACTIONAL_MINIMUM',
      'PREVIEW_MARKET_ORDERS_PROHIBITED_DURING_NON_CORE_SESSION',
      'PREVIEW_NOTIONAL_ORDERS_PROHIBITED_DURING_NON_CORE_SESSION',
      'PREVIEW_MAX_NOTIONAL_PER_ORDER_BREACHED_15C35_CHECK',
      'PREVIEW_MAX_SHARES_PER_ORDER_BREACHED_15C35_CHECK',
      'PREVIEW_INVALID_EQUITY_TRADING_SESSION',
      'PREVIEW_PRODUCT_TRADING_HALTED',
      'PREVIEW_TRADING_DISABLED',
      'PREVIEW_INVALID_BRACKET_LIMIT_PRICE_PRECISION',
      'PREVIEW_SCALED_PARAM_DISCREPANCY',
      'PREVIEW_STOP_LOSS_PRICE_TOO_LOW',
      'PREVIEW_PREDICTIONS_QUOTE_SIZE_BELOW_MIN_CONTRACT_PRICE',
      'PREVIEW_PREDICTIONS_HIGH_PRICE_CONTRACTS_BLOCKED',
      'PREVIEW_ATTACHED_STOP_LOSS_PRICE_TOO_LOW',
      'PREVIEW_BREACHED_RISK_LIMIT',
      'PREVIEW_STOP_LOSS_PRICE_TOO_HIGH',
      'PREVIEW_ATTACHED_STOP_LOSS_PRICE_TOO_HIGH',
      'PREVIEW_TAKE_PROFIT_PRICE_TOO_HIGH',
      'PREVIEW_ATTACHED_TAKE_PROFIT_PRICE_TOO_HIGH',
      'PREVIEW_TAKE_PROFIT_PRICE_TOO_LOW',
      'PREVIEW_ATTACHED_TAKE_PROFIT_PRICE_TOO_LOW',
      'PREVIEW_INVALID_UNSUPPORTED_INSTRUMENT',
    ]
  ]
  """Machine-readable preview-validation failure code."""


class StopLimitStopLimitGtc(TypedDict):
  """StopLimitStopLimitGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_price: str
  """Last trade price that triggers the order."""
  stop_direction: Literal['STOP_DIRECTION_STOP_UP', 'STOP_DIRECTION_STOP_DOWN']
  """Which way the last trade price must cross `stop_price` to trigger."""


class TriggerBracketGtc(TypedDict):
  """TriggerBracketGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_trigger_price: str
  """Price (in quote currency) at which the position is exited; the resulting stop-limit order's limit price is 5% beyond it (higher for buys, lower for sells)."""


class TriggerBracketPnl(TypedDict):
  """Estimated profit/loss at each leg of a bracket order."""

  take_profit_pnl: NotRequired[str]
  """PnL if the order fills at the take-profit price."""
  stop_loss_pnl: NotRequired[str]
  """PnL if the order fills at the stop-loss price."""


class LimitLimitGtc(TypedDict):
  """LimitLimitGtc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  post_only: NotRequired[bool]
  """Only post liquidity; reject rather than take."""
  currency_size: NotRequired[Amount]


class PnlConfiguration(TypedDict):
  trigger_bracket_pnl: NotRequired[TriggerBracketPnl]


class StopLimitStopLimitGtcConfiguration(TypedDict):
  """Stop-limit order, good-till-cancelled: becomes a limit order once the last trade price crosses `stop_price`."""

  stop_limit_stop_limit_gtc: StopLimitStopLimitGtc


class TriggerBracketGtcConfiguration(TypedDict):
  """Bracket order, good-till-cancelled: a limit order with an embedded take-profit/stop-loss exit at `stop_trigger_price`."""

  trigger_bracket_gtc: TriggerBracketGtc


class EditOrderPreviewResponse(TypedDict):
  errors: list[EditOrderPreviewError]
  """Errors that would prevent this edit, if any."""
  slippage: NotRequired[str]
  """Estimated price slippage from the proposed edit."""
  order_total: NotRequired[str]
  """Total order value after the proposed edit."""
  commission_total: NotRequired[str]
  """Total commission after the proposed edit."""
  quote_size: NotRequired[str]
  """Quote-currency amount after the proposed edit."""
  base_size: NotRequired[str]
  """Base-currency amount after the proposed edit."""
  best_bid: NotRequired[str]
  """Current best bid price."""
  best_ask: NotRequired[str]
  """Current best ask price."""
  average_filled_price: NotRequired[str]
  """Average price of the portion already filled."""
  order_margin_total: NotRequired[str]
  """Total margin requirement after the proposed edit."""
  commission_detail_total: NotRequired[CommissionDetailTotal | None]
  """Breakdown of commission after the proposed edit. Verified live: returns null when not applicable."""
  pnl_configuration: NotRequired[PnlConfiguration | None]
  """Estimated profit/loss for the order after the proposed edit. An estimate; excludes fees and slippage. Verified live: returns null when not applicable."""


class LimitLimitGtcConfiguration(TypedDict):
  """Limit order, good-till-cancelled: remains on the order book until filled or cancelled."""

  limit_limit_gtc: LimitLimitGtc


@dataclass(frozen=True, kw_only=True)
class EditPreview(RpcEndpoint):
  """`POST /api/v3/brokerage/orders/edit_preview`."""

  async def __call__(
    self,
    *,
    order_id: str,
    price: str,
    size: str,
    attached_order_configuration: LimitLimitGtcConfiguration
    | StopLimitStopLimitGtcConfiguration
    | TriggerBracketGtcConfiguration
    | None = None,
    cancel_attached_order: bool | None = None,
    stop_price: str | None = None,
    average_entry_price: str | None = None,
  ) -> EditOrderPreviewResponse:
    """Preview the effect of editing an open order's price/size, without submitting the edit. Same request shape as `edit`.

    Args:
      order_id: Id of the order to preview editing.
      price: The order's proposed new price, e.g. `"19000.00"`.
      size: The order's proposed new size, e.g. `"0.001"`.
      attached_order_configuration: Proposed configuration for an attached bracket order; only `trigger_bracket_gtc`, `limit_limit_gtc`, and `stop_limit_stop_limit_gtc` are eligible.
      cancel_attached_order: Preview dropping both take-profit and stop-loss legs, converting the order to a plain limit order.
      stop_price: Proposed new stop price, for a stop or take-profit/stop-loss order.
      average_entry_price: Average entry price to use for estimated PnL, e.g. `"18000.00"`.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/orders/edit-order-preview)
    """
    body: dict = {
      'order_id': order_id,
      'price': price,
      'size': size,
    }
    if attached_order_configuration is not None:
      body['attached_order_configuration'] = attached_order_configuration
    if cancel_attached_order is not None:
      body['cancel_attached_order'] = cancel_attached_order
    if stop_price is not None:
      body['stop_price'] = stop_price
    if average_entry_price is not None:
      body['average_entry_price'] = average_entry_price
    return await self.authed_request(
      'POST',
      '/api/v3/brokerage/orders/edit_preview',
      json=body,
      validator=validator(EditOrderPreviewResponse),
    )
