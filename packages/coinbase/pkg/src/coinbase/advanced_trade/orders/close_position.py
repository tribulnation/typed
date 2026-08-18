from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class Amount0OrderConfigurationAnyOf0MarketMarketIocCurrencySize(TypedDict):
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""

  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class Amount0OrderConfigurationAnyOf3LimitLimitGtcCurrencySize(TypedDict):
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""

  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class Amount0OrderConfigurationAnyOf4LimitLimitGtdCurrencySize(TypedDict):
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""

  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class Amount1OrderConfigurationAnyOf0MarketMarketIocCurrencySize(TypedDict):
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""

  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class Amount1OrderConfigurationAnyOf3LimitLimitGtcCurrencySize(TypedDict):
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""

  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class Amount1OrderConfigurationAnyOf4LimitLimitGtdCurrencySize(TypedDict):
  """`quote_size` converted to the account's native currency. Empty when the order is not sized in quote or when rates are unavailable."""

  value: str
  """Amount of currency, as a decimal string."""
  currency: str
  """Currency code, e.g. `BTC`."""


class LimitLimitFok0OrderConfigurationAnyOf5LimitLimitFok(TypedDict):
  """LimitLimitFok fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""


class LimitLimitFok1OrderConfigurationAnyOf5LimitLimitFok(TypedDict):
  """LimitLimitFok fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""


class MarketMarketFok0OrderConfigurationAnyOf1MarketMarketFok(TypedDict):
  """MarketMarketFok fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""


class MarketMarketFok1OrderConfigurationAnyOf1MarketMarketFok(TypedDict):
  """MarketMarketFok fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""


class NewOrderErrorResponse(TypedDict):
  """Why the closing order failed to be created."""

  error: NotRequired[
    Literal[
      'UNKNOWN_FAILURE_REASON',
      'UNSUPPORTED_ORDER_CONFIGURATION',
      'INVALID_SIDE',
      'INVALID_PRODUCT_ID',
      'INVALID_SIZE_PRECISION',
      'INVALID_PRICE_PRECISION',
      'INSUFFICIENT_FUND',
      'INVALID_LEDGER_BALANCE',
      'ORDER_ENTRY_DISABLED',
      'INELIGIBLE_PAIR',
      'INVALID_LIMIT_PRICE_POST_ONLY',
      'INVALID_LIMIT_PRICE',
      'INVALID_NO_LIQUIDITY',
      'INVALID_REQUEST',
      'COMMANDER_REJECTED_NEW_ORDER',
      'INSUFFICIENT_FUNDS',
      'IN_LIQUIDATION',
      'INVALID_MARGIN_TYPE',
      'INVALID_LEVERAGE',
      'UNTRADABLE_PRODUCT',
      'INVALID_FCM_TRADING_SESSION',
      'GEOFENCING_RESTRICTION',
      'QUOTE_SIZE_NOT_ALLOWED_FOR_BRACKET',
      'INVALID_BRACKET_PRICES',
      'MISSING_MARKET_TRADE_DATA',
      'INVALID_BRACKET_LIMIT_PRICE',
      'INVALID_BRACKET_STOP_TRIGGER_PRICE',
      'BRACKET_LIMIT_PRICE_OUT_OF_BOUNDS',
      'STOP_TRIGGER_PRICE_OUT_OF_BOUNDS',
      'BRACKET_ORDER_NOT_SUPPORTED',
      'FOK_DISABLED',
      'FOK_ONLY_ALLOWED_ON_LIMIT_ORDERS',
      'POST_ONLY_NOT_ALLOWED_WITH_FOK',
      'UBO_HIGH_LEVERAGE_QUANTITY_BREACHED',
      'END_TIME_TOO_FAR_IN_FUTURE',
      'LIMIT_PRICE_TOO_FAR_FROM_MARKET',
      'OPEN_BRACKET_ORDERS',
      'FUTURES_AFTER_HOUR_INVALID_ORDER_TYPE',
      'FUTURES_AFTER_HOUR_INVALID_TIME_IN_FORCE',
      'INVALID_ATTACHED_TAKE_PROFIT_PRICE',
      'INVALID_ATTACHED_STOP_LOSS_PRICE',
      'INVALID_ATTACHED_TAKE_PROFIT_PRICE_PRECISION',
      'INVALID_ATTACHED_STOP_LOSS_PRICE_PRECISION',
      'INVALID_ATTACHED_TAKE_PROFIT_PRICE_OUT_OF_BOUNDS',
      'INVALID_ATTACHED_STOP_LOSS_PRICE_OUT_OF_BOUNDS',
      'INVALID_ATTACHED_TAKE_PROFIT_PRICE_EXCEEDS_MAX_DISTANCE_FROM_ORIGINATING_PRICE',
      'INVALID_ATTACHED_TAKE_PROFIT_SIZE_BELOW_MIN',
      'ATTACHED_ORDER_SIZE_MUST_BE_NIL',
      'INVALID_SETTLEMENT_CURRENCY',
      'DURATION_TOO_SMALL',
      'INTX_FOK_ONLY_ALLOWED_ON_LIMIT_AND_MARKET_ORDERS',
      'BUCKET_SIZE_SMALLER_THAN_QUOTE_MIN',
      'BUCKET_SIZE_SMALLER_THAN_BASE_MIN',
      'END_TIME_AFTER_CONTRACT_EXPIRATION',
      'START_TIME_MUST_BE_SPECIFIED',
      'ICEBERG_ORDERS_NOT_SUPPORTED',
      'END_TIME_IS_IN_THE_PAST',
      'GTD_ORDERS_MUST_HAVE_END_TIME',
      'ATTACHED_ORDER_MUST_HAVE_POSITIVE_PRICES',
      'INVALID_ORDER_SIDE_FOR_ATTACHED_TPSL',
      'ATTACHED_ORDERS_ONLY_ALLOWED_ON_MARKET_LIMIT',
      'INVALID_ORDER_TYPE_FOR_ATTACHED',
      'PRICE_NOT_ALLOWED_FOR_MARKET_ORDERS',
      'REDUCE_ONLY_NOT_ALLOWED_ON_VENUE',
      'DURATION_TOO_LARGE',
      'REDUCE_ONLY_NOT_ALLOWED_ON_SPOT_PRODUCTS',
      'LIMIT_ORDER_PRICE_EXCEEDS_PRICE_BAND_ON_BUY',
      'LIMIT_ORDER_PRICE_EXCEEDS_PRICE_BAND_ON_SELL',
      'INVALID_ATTACHED_TAKE_PROFIT_PRICE_OUT_OF_BOUNDS_ON_AGGRESSIVE_ORDER',
      'INVALID_ATTACHED_STOP_LOSS_PRICE_OUT_OF_BOUNDS_ON_AGGRESSIVE_ORDER',
      'STOP_ALREADY_TRIGGERED',
      'REPLACE_NOT_SUPPORTED',
      'ORDER_IS_PENDING_CANCEL',
      'POSITION_SIZE_INCREASE_REJECT',
      'ASSET_BALANCE_INCREASE_REJECT',
      'TOO_MANY_PENDING_REPLACES',
      'INVALID_RFQ_BASE_SIZE_TOO_SMALL',
      'INVALID_RFQ_BASE_SIZE_TOO_LARGE',
      'INVALID_RFQ_QUOTE_SIZE_TOO_SMALL',
      'INVALID_RFQ_QUOTE_SIZE_TOO_LARGE',
      'INVALID_UNSUPPORTED_INSTRUMENT',
      'REDUCE_ONLY_INCREASED_POSITION_SIZE',
      'SCALED_PARAM_INFEASIBLE',
      'SCALED_MIN_ORDER_VIOLATION',
      'SCALED_MAX_ORDER_VIOLATION',
      'POST_ONLY_NOT_ALLOWED_WITH_PEG',
      'INVALID_PEG_OFFSET',
      'INVALID_PEG_WIG_LEVEL',
      'INVALID_PEG_VENUE_OPTIONS',
      'PEG_INVALID_ORDER_TYPE',
      'SINGLE_LEGGED_TPSL_NOT_ALLOWED',
      'FRACTIONAL_ORDERS_NOT_ALLOWED_FOR_PRODUCT',
      'QUOTE_ORDERS_NOT_ALLOWED_FOR_PRODUCT',
      'NBBO_NOT_PROVIDED',
      'INVALID_NBBO_BID_PRICE',
      'INVALID_NBBO_ASK_PRICE',
      'NOTIONAL_SIZE_BREACHES_FRACTIONAL_MINIMUM',
      'MARKET_ORDERS_PROHIBITED_DURING_NON_CORE_SESSION',
      'NOTIONAL_ORDERS_PROHIBITED_DURING_NON_CORE_SESSION',
      'MAX_NOTIONAL_PER_ORDER_BREACHED_15C35_CHECK',
      'MAX_SHARES_PER_ORDER_BREACHED_15C35_CHECK',
      'INVALID_EQUITY_TRADING_SESSION',
      'PRODUCT_TRADING_HALTED',
      'TRADING_DISABLED',
      'CANNOT_CLOSE_ZERO_POSITION',
      'SCALED_PARAM_DISCREPANCY',
      'STOP_LOSS_PRICE_TOO_LOW',
      'ATTACHED_STOP_LOSS_PRICE_TOO_LOW',
      'BREACHED_RISK_LIMIT',
      'STOP_LOSS_PRICE_TOO_HIGH',
      'ATTACHED_STOP_LOSS_PRICE_TOO_HIGH',
      'TAKE_PROFIT_PRICE_TOO_HIGH',
      'ATTACHED_TAKE_PROFIT_PRICE_TOO_HIGH',
      'TAKE_PROFIT_PRICE_TOO_LOW',
      'ATTACHED_TAKE_PROFIT_PRICE_TOO_LOW',
      'MODIFY_POSITION_WORKFLOW_ALREADY_RUNNING',
      'DUPLICATE_CLIENT_ORDER_ID',
      'RFQ_QUOTE_EXPIRED',
      'RFQ_TOO_MANY_OPEN_QUOTES',
      'RFQ_RATE_LIMITED',
      'RFQ_INVALID_COMBO_LEGS',
      'RFQ_VALIDATION_FAILURE',
      'RFQ_VENUE_REJECTED',
    ]
  ]
  """Deprecated failure code; superseded by `new_order_failure_reason`."""
  message: NotRequired[str]
  """Generic error explanation."""
  error_details: NotRequired[str]
  """Descriptive error message."""
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
  """Deprecated preview-validation failure code."""
  new_order_failure_reason: Literal[
    'UNKNOWN_FAILURE_REASON',
    'UNSUPPORTED_ORDER_CONFIGURATION',
    'INVALID_SIDE',
    'INVALID_PRODUCT_ID',
    'INVALID_SIZE_PRECISION',
    'INVALID_PRICE_PRECISION',
    'INSUFFICIENT_FUND',
    'INVALID_LEDGER_BALANCE',
    'ORDER_ENTRY_DISABLED',
    'INELIGIBLE_PAIR',
    'INVALID_LIMIT_PRICE_POST_ONLY',
    'INVALID_LIMIT_PRICE',
    'INVALID_NO_LIQUIDITY',
    'INVALID_REQUEST',
    'COMMANDER_REJECTED_NEW_ORDER',
    'INSUFFICIENT_FUNDS',
    'IN_LIQUIDATION',
    'INVALID_MARGIN_TYPE',
    'INVALID_LEVERAGE',
    'UNTRADABLE_PRODUCT',
    'INVALID_FCM_TRADING_SESSION',
    'GEOFENCING_RESTRICTION',
    'QUOTE_SIZE_NOT_ALLOWED_FOR_BRACKET',
    'INVALID_BRACKET_PRICES',
    'MISSING_MARKET_TRADE_DATA',
    'INVALID_BRACKET_LIMIT_PRICE',
    'INVALID_BRACKET_STOP_TRIGGER_PRICE',
    'BRACKET_LIMIT_PRICE_OUT_OF_BOUNDS',
    'STOP_TRIGGER_PRICE_OUT_OF_BOUNDS',
    'BRACKET_ORDER_NOT_SUPPORTED',
    'FOK_DISABLED',
    'FOK_ONLY_ALLOWED_ON_LIMIT_ORDERS',
    'POST_ONLY_NOT_ALLOWED_WITH_FOK',
    'UBO_HIGH_LEVERAGE_QUANTITY_BREACHED',
    'END_TIME_TOO_FAR_IN_FUTURE',
    'LIMIT_PRICE_TOO_FAR_FROM_MARKET',
    'OPEN_BRACKET_ORDERS',
    'FUTURES_AFTER_HOUR_INVALID_ORDER_TYPE',
    'FUTURES_AFTER_HOUR_INVALID_TIME_IN_FORCE',
    'INVALID_ATTACHED_TAKE_PROFIT_PRICE',
    'INVALID_ATTACHED_STOP_LOSS_PRICE',
    'INVALID_ATTACHED_TAKE_PROFIT_PRICE_PRECISION',
    'INVALID_ATTACHED_STOP_LOSS_PRICE_PRECISION',
    'INVALID_ATTACHED_TAKE_PROFIT_PRICE_OUT_OF_BOUNDS',
    'INVALID_ATTACHED_STOP_LOSS_PRICE_OUT_OF_BOUNDS',
    'INVALID_ATTACHED_TAKE_PROFIT_PRICE_EXCEEDS_MAX_DISTANCE_FROM_ORIGINATING_PRICE',
    'INVALID_ATTACHED_TAKE_PROFIT_SIZE_BELOW_MIN',
    'ATTACHED_ORDER_SIZE_MUST_BE_NIL',
    'INVALID_SETTLEMENT_CURRENCY',
    'DURATION_TOO_SMALL',
    'INTX_FOK_ONLY_ALLOWED_ON_LIMIT_AND_MARKET_ORDERS',
    'BUCKET_SIZE_SMALLER_THAN_QUOTE_MIN',
    'BUCKET_SIZE_SMALLER_THAN_BASE_MIN',
    'END_TIME_AFTER_CONTRACT_EXPIRATION',
    'START_TIME_MUST_BE_SPECIFIED',
    'ICEBERG_ORDERS_NOT_SUPPORTED',
    'END_TIME_IS_IN_THE_PAST',
    'GTD_ORDERS_MUST_HAVE_END_TIME',
    'ATTACHED_ORDER_MUST_HAVE_POSITIVE_PRICES',
    'INVALID_ORDER_SIDE_FOR_ATTACHED_TPSL',
    'ATTACHED_ORDERS_ONLY_ALLOWED_ON_MARKET_LIMIT',
    'INVALID_ORDER_TYPE_FOR_ATTACHED',
    'PRICE_NOT_ALLOWED_FOR_MARKET_ORDERS',
    'REDUCE_ONLY_NOT_ALLOWED_ON_VENUE',
    'DURATION_TOO_LARGE',
    'REDUCE_ONLY_NOT_ALLOWED_ON_SPOT_PRODUCTS',
    'LIMIT_ORDER_PRICE_EXCEEDS_PRICE_BAND_ON_BUY',
    'LIMIT_ORDER_PRICE_EXCEEDS_PRICE_BAND_ON_SELL',
    'INVALID_ATTACHED_TAKE_PROFIT_PRICE_OUT_OF_BOUNDS_ON_AGGRESSIVE_ORDER',
    'INVALID_ATTACHED_STOP_LOSS_PRICE_OUT_OF_BOUNDS_ON_AGGRESSIVE_ORDER',
    'STOP_ALREADY_TRIGGERED',
    'REPLACE_NOT_SUPPORTED',
    'ORDER_IS_PENDING_CANCEL',
    'POSITION_SIZE_INCREASE_REJECT',
    'ASSET_BALANCE_INCREASE_REJECT',
    'TOO_MANY_PENDING_REPLACES',
    'INVALID_RFQ_BASE_SIZE_TOO_SMALL',
    'INVALID_RFQ_BASE_SIZE_TOO_LARGE',
    'INVALID_RFQ_QUOTE_SIZE_TOO_SMALL',
    'INVALID_RFQ_QUOTE_SIZE_TOO_LARGE',
    'INVALID_UNSUPPORTED_INSTRUMENT',
    'REDUCE_ONLY_INCREASED_POSITION_SIZE',
    'SCALED_PARAM_INFEASIBLE',
    'SCALED_MIN_ORDER_VIOLATION',
    'SCALED_MAX_ORDER_VIOLATION',
    'POST_ONLY_NOT_ALLOWED_WITH_PEG',
    'INVALID_PEG_OFFSET',
    'INVALID_PEG_WIG_LEVEL',
    'INVALID_PEG_VENUE_OPTIONS',
    'PEG_INVALID_ORDER_TYPE',
    'SINGLE_LEGGED_TPSL_NOT_ALLOWED',
    'FRACTIONAL_ORDERS_NOT_ALLOWED_FOR_PRODUCT',
    'QUOTE_ORDERS_NOT_ALLOWED_FOR_PRODUCT',
    'NBBO_NOT_PROVIDED',
    'INVALID_NBBO_BID_PRICE',
    'INVALID_NBBO_ASK_PRICE',
    'NOTIONAL_SIZE_BREACHES_FRACTIONAL_MINIMUM',
    'MARKET_ORDERS_PROHIBITED_DURING_NON_CORE_SESSION',
    'NOTIONAL_ORDERS_PROHIBITED_DURING_NON_CORE_SESSION',
    'MAX_NOTIONAL_PER_ORDER_BREACHED_15C35_CHECK',
    'MAX_SHARES_PER_ORDER_BREACHED_15C35_CHECK',
    'INVALID_EQUITY_TRADING_SESSION',
    'PRODUCT_TRADING_HALTED',
    'TRADING_DISABLED',
    'CANNOT_CLOSE_ZERO_POSITION',
    'SCALED_PARAM_DISCREPANCY',
    'STOP_LOSS_PRICE_TOO_LOW',
    'ATTACHED_STOP_LOSS_PRICE_TOO_LOW',
    'BREACHED_RISK_LIMIT',
    'STOP_LOSS_PRICE_TOO_HIGH',
    'ATTACHED_STOP_LOSS_PRICE_TOO_HIGH',
    'TAKE_PROFIT_PRICE_TOO_HIGH',
    'ATTACHED_TAKE_PROFIT_PRICE_TOO_HIGH',
    'TAKE_PROFIT_PRICE_TOO_LOW',
    'ATTACHED_TAKE_PROFIT_PRICE_TOO_LOW',
    'MODIFY_POSITION_WORKFLOW_ALREADY_RUNNING',
    'DUPLICATE_CLIENT_ORDER_ID',
    'RFQ_QUOTE_EXPIRED',
    'RFQ_TOO_MANY_OPEN_QUOTES',
    'RFQ_RATE_LIMITED',
    'RFQ_INVALID_COMBO_LEGS',
    'RFQ_VALIDATION_FAILURE',
    'RFQ_VENUE_REJECTED',
  ]
  """Why order creation failed."""


class NewOrderSuccessResponse(TypedDict):
  """The created closing order's identifiers."""

  order_id: str
  """The created order's unique id."""
  product_id: NotRequired[str]
  """Trading pair the order was placed on."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Trade direction of the closing order."""
  client_order_id: NotRequired[str]
  """The caller-supplied unique id echoed back."""


class ScaledOrderLeg0OrderConfigurationAnyOf11ScaledLimitGtcOrdersItem(TypedDict):
  """One child limit order in a scaled order."""

  base_size: NotRequired[str]
  """Base-currency amount for this leg."""
  limit_price: NotRequired[str]
  """Limit price for this leg."""


class ScaledOrderLeg1OrderConfigurationAnyOf11ScaledLimitGtcOrdersItem(TypedDict):
  """One child limit order in a scaled order."""

  base_size: NotRequired[str]
  """Base-currency amount for this leg."""
  limit_price: NotRequired[str]
  """Limit price for this leg."""


class SorLimitIoc0OrderConfigurationAnyOf2SorLimitIoc(TypedDict):
  """SorLimitIoc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""


class SorLimitIoc1OrderConfigurationAnyOf2SorLimitIoc(TypedDict):
  """SorLimitIoc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""


class StopLimitStopLimitGtc0OrderConfigurationAnyOf7StopLimitStopLimitGtc(TypedDict):
  """StopLimitStopLimitGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_price: str
  """Last trade price that triggers the order."""
  stop_direction: Literal['STOP_DIRECTION_STOP_UP', 'STOP_DIRECTION_STOP_DOWN']
  """Which way the last trade price must cross `stop_price` to trigger."""


class StopLimitStopLimitGtc1OrderConfigurationAnyOf7StopLimitStopLimitGtc(TypedDict):
  """StopLimitStopLimitGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_price: str
  """Last trade price that triggers the order."""
  stop_direction: Literal['STOP_DIRECTION_STOP_UP', 'STOP_DIRECTION_STOP_DOWN']
  """Which way the last trade price must cross `stop_price` to trigger."""


class StopLimitStopLimitGtd0OrderConfigurationAnyOf8StopLimitStopLimitGtd(TypedDict):
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


class StopLimitStopLimitGtd1OrderConfigurationAnyOf8StopLimitStopLimitGtd(TypedDict):
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


class TriggerBracketGtc0OrderConfigurationAnyOf9TriggerBracketGtc(TypedDict):
  """TriggerBracketGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_trigger_price: str
  """Price (in quote currency) at which the position is exited; the resulting stop-limit order's limit price is 5% beyond it (higher for buys, lower for sells)."""


class TriggerBracketGtc1OrderConfigurationAnyOf9TriggerBracketGtc(TypedDict):
  """TriggerBracketGtc fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_trigger_price: str
  """Price (in quote currency) at which the position is exited; the resulting stop-limit order's limit price is 5% beyond it (higher for buys, lower for sells)."""


class TriggerBracketGtd0OrderConfigurationAnyOf10TriggerBracketGtd(TypedDict):
  """TriggerBracketGtd fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_trigger_price: str
  """Price (in quote currency) at which the position is exited; the resulting stop-limit order's limit price is 5% beyond it (higher for buys, lower for sells)."""
  end_time: str
  """RFC3339 time after which the order expires if unfilled."""


class TriggerBracketGtd1OrderConfigurationAnyOf10TriggerBracketGtd(TypedDict):
  """TriggerBracketGtd fields."""

  base_size: str
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  stop_trigger_price: str
  """Price (in quote currency) at which the position is exited; the resulting stop-limit order's limit price is 5% beyond it (higher for buys, lower for sells)."""
  end_time: str
  """RFC3339 time after which the order expires if unfilled."""


class TwapLimitGtd0OrderConfigurationAnyOf6TwapLimitGtd(TypedDict):
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


class TwapLimitGtd1OrderConfigurationAnyOf6TwapLimitGtd(TypedDict):
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


class LimitLimitFokConfiguration0OrderConfigurationAnyOf5(TypedDict):
  """Limit order, fill-or-kill: posts only if it fills immediately and completely."""

  limit_limit_fok: LimitLimitFok0OrderConfigurationAnyOf5LimitLimitFok


class LimitLimitFokConfiguration1OrderConfigurationAnyOf5(TypedDict):
  """Limit order, fill-or-kill: posts only if it fills immediately and completely."""

  limit_limit_fok: LimitLimitFok1OrderConfigurationAnyOf5LimitLimitFok


class LimitLimitGtc0OrderConfigurationAnyOf3LimitLimitGtc(TypedDict):
  """LimitLimitGtc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  post_only: NotRequired[bool]
  """Only post liquidity; reject rather than take."""
  currency_size: NotRequired[Amount0OrderConfigurationAnyOf3LimitLimitGtcCurrencySize]


class LimitLimitGtc1OrderConfigurationAnyOf3LimitLimitGtc(TypedDict):
  """LimitLimitGtc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  limit_price: str
  """Worst execution price threshold. A buy fills at or below it, a sell at or above it."""
  post_only: NotRequired[bool]
  """Only post liquidity; reject rather than take."""
  currency_size: NotRequired[Amount1OrderConfigurationAnyOf3LimitLimitGtcCurrencySize]


class LimitLimitGtd0OrderConfigurationAnyOf4LimitLimitGtd(TypedDict):
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
  currency_size: NotRequired[Amount0OrderConfigurationAnyOf4LimitLimitGtdCurrencySize]


class LimitLimitGtd1OrderConfigurationAnyOf4LimitLimitGtd(TypedDict):
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
  currency_size: NotRequired[Amount1OrderConfigurationAnyOf4LimitLimitGtdCurrencySize]


class MarketMarketFokConfiguration0OrderConfigurationAnyOf1(TypedDict):
  """Market order, fill-or-kill: posts only if it fills immediately and completely."""

  market_market_fok: MarketMarketFok0OrderConfigurationAnyOf1MarketMarketFok


class MarketMarketFokConfiguration1OrderConfigurationAnyOf1(TypedDict):
  """Market order, fill-or-kill: posts only if it fills immediately and completely."""

  market_market_fok: MarketMarketFok1OrderConfigurationAnyOf1MarketMarketFok


class MarketMarketIoc0OrderConfigurationAnyOf0MarketMarketIoc(TypedDict):
  """MarketMarketIoc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  currency_size: NotRequired[Amount0OrderConfigurationAnyOf0MarketMarketIocCurrencySize]


class MarketMarketIoc1OrderConfigurationAnyOf0MarketMarketIoc(TypedDict):
  """MarketMarketIoc fields."""

  quote_size: NotRequired[str]
  """Quote-currency amount. One of `quote_size`/`base_size` is required."""
  base_size: NotRequired[str]
  """Base-currency amount. One of `quote_size`/`base_size` is required."""
  currency_size: NotRequired[Amount1OrderConfigurationAnyOf0MarketMarketIocCurrencySize]


class ScaledLimitGtc0OrderConfigurationAnyOf11ScaledLimitGtc(TypedDict):
  """ScaledLimitGtc fields."""

  orders: NotRequired[
    list[ScaledOrderLeg0OrderConfigurationAnyOf11ScaledLimitGtcOrdersItem]
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


class ScaledLimitGtc1OrderConfigurationAnyOf11ScaledLimitGtc(TypedDict):
  """ScaledLimitGtc fields."""

  orders: NotRequired[
    list[ScaledOrderLeg1OrderConfigurationAnyOf11ScaledLimitGtcOrdersItem]
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


class SorLimitIocConfiguration0OrderConfigurationAnyOf2(TypedDict):
  """Smart-order-routed limit order, immediate-or-cancel: posts only if it fills immediately, any unfilled remainder is cancelled."""

  sor_limit_ioc: SorLimitIoc0OrderConfigurationAnyOf2SorLimitIoc


class SorLimitIocConfiguration1OrderConfigurationAnyOf2(TypedDict):
  """Smart-order-routed limit order, immediate-or-cancel: posts only if it fills immediately, any unfilled remainder is cancelled."""

  sor_limit_ioc: SorLimitIoc1OrderConfigurationAnyOf2SorLimitIoc


class StopLimitStopLimitGtcConfiguration0OrderConfigurationAnyOf7(TypedDict):
  """Stop-limit order, good-till-cancelled: becomes a limit order once the last trade price crosses `stop_price`."""

  stop_limit_stop_limit_gtc: (
    StopLimitStopLimitGtc0OrderConfigurationAnyOf7StopLimitStopLimitGtc
  )


class StopLimitStopLimitGtcConfiguration1OrderConfigurationAnyOf7(TypedDict):
  """Stop-limit order, good-till-cancelled: becomes a limit order once the last trade price crosses `stop_price`."""

  stop_limit_stop_limit_gtc: (
    StopLimitStopLimitGtc1OrderConfigurationAnyOf7StopLimitStopLimitGtc
  )


class StopLimitStopLimitGtdConfiguration0OrderConfigurationAnyOf8(TypedDict):
  """Stop-limit order, good-till-date: becomes a limit order once the last trade price crosses `stop_price`, or expires at `end_time`."""

  stop_limit_stop_limit_gtd: (
    StopLimitStopLimitGtd0OrderConfigurationAnyOf8StopLimitStopLimitGtd
  )


class StopLimitStopLimitGtdConfiguration1OrderConfigurationAnyOf8(TypedDict):
  """Stop-limit order, good-till-date: becomes a limit order once the last trade price crosses `stop_price`, or expires at `end_time`."""

  stop_limit_stop_limit_gtd: (
    StopLimitStopLimitGtd1OrderConfigurationAnyOf8StopLimitStopLimitGtd
  )


class TriggerBracketGtcConfiguration0OrderConfigurationAnyOf9(TypedDict):
  """Bracket order, good-till-cancelled: a limit order with an embedded take-profit/stop-loss exit at `stop_trigger_price`."""

  trigger_bracket_gtc: TriggerBracketGtc0OrderConfigurationAnyOf9TriggerBracketGtc


class TriggerBracketGtcConfiguration1OrderConfigurationAnyOf9(TypedDict):
  """Bracket order, good-till-cancelled: a limit order with an embedded take-profit/stop-loss exit at `stop_trigger_price`."""

  trigger_bracket_gtc: TriggerBracketGtc1OrderConfigurationAnyOf9TriggerBracketGtc


class TriggerBracketGtdConfiguration0OrderConfigurationAnyOf10(TypedDict):
  """Bracket order, good-till-date: a limit order with an embedded take-profit/stop-loss exit at `stop_trigger_price`, expiring at `end_time`."""

  trigger_bracket_gtd: TriggerBracketGtd0OrderConfigurationAnyOf10TriggerBracketGtd


class TriggerBracketGtdConfiguration1OrderConfigurationAnyOf10(TypedDict):
  """Bracket order, good-till-date: a limit order with an embedded take-profit/stop-loss exit at `stop_trigger_price`, expiring at `end_time`."""

  trigger_bracket_gtd: TriggerBracketGtd1OrderConfigurationAnyOf10TriggerBracketGtd


class TwapLimitGtdConfiguration0OrderConfigurationAnyOf6(TypedDict):
  """Time-weighted-average-price order: splits execution into equal-sized limit suborders spread across a time window."""

  twap_limit_gtd: TwapLimitGtd0OrderConfigurationAnyOf6TwapLimitGtd


class TwapLimitGtdConfiguration1OrderConfigurationAnyOf6(TypedDict):
  """Time-weighted-average-price order: splits execution into equal-sized limit suborders spread across a time window."""

  twap_limit_gtd: TwapLimitGtd1OrderConfigurationAnyOf6TwapLimitGtd


class LimitLimitGtcConfiguration0OrderConfigurationAnyOf3(TypedDict):
  """Limit order, good-till-cancelled: remains on the order book until filled or cancelled."""

  limit_limit_gtc: LimitLimitGtc0OrderConfigurationAnyOf3LimitLimitGtc


class LimitLimitGtcConfiguration1OrderConfigurationAnyOf3(TypedDict):
  """Limit order, good-till-cancelled: remains on the order book until filled or cancelled."""

  limit_limit_gtc: LimitLimitGtc1OrderConfigurationAnyOf3LimitLimitGtc


class LimitLimitGtdConfiguration0OrderConfigurationAnyOf4(TypedDict):
  """Limit order, good-till-date: remains on the order book until filled, cancelled, or `end_time`."""

  limit_limit_gtd: LimitLimitGtd0OrderConfigurationAnyOf4LimitLimitGtd


class LimitLimitGtdConfiguration1OrderConfigurationAnyOf4(TypedDict):
  """Limit order, good-till-date: remains on the order book until filled, cancelled, or `end_time`."""

  limit_limit_gtd: LimitLimitGtd1OrderConfigurationAnyOf4LimitLimitGtd


class MarketMarketIocConfiguration0OrderConfigurationAnyOf0(TypedDict):
  """Market order, immediate-or-cancel: fills at the current best available price, any unfilled remainder is cancelled."""

  market_market_ioc: MarketMarketIoc0OrderConfigurationAnyOf0MarketMarketIoc


class MarketMarketIocConfiguration1OrderConfigurationAnyOf0(TypedDict):
  """Market order, immediate-or-cancel: fills at the current best available price, any unfilled remainder is cancelled."""

  market_market_ioc: MarketMarketIoc1OrderConfigurationAnyOf0MarketMarketIoc


class ScaledLimitGtcConfiguration0OrderConfigurationAnyOf11(TypedDict):
  """Scaled order, good-till-cancelled: a ladder of limit child orders spread across a price range."""

  scaled_limit_gtc: ScaledLimitGtc0OrderConfigurationAnyOf11ScaledLimitGtc


class ScaledLimitGtcConfiguration1OrderConfigurationAnyOf11(TypedDict):
  """Scaled order, good-till-cancelled: a ladder of limit child orders spread across a price range."""

  scaled_limit_gtc: ScaledLimitGtc1OrderConfigurationAnyOf11ScaledLimitGtc


class ClosePositionFailure(TypedDict):
  success: bool
  """Whether the closing order was created."""
  error_response: NewOrderErrorResponse
  order_configuration: NotRequired[
    MarketMarketIocConfiguration1OrderConfigurationAnyOf0
    | MarketMarketFokConfiguration1OrderConfigurationAnyOf1
    | SorLimitIocConfiguration1OrderConfigurationAnyOf2
    | LimitLimitGtcConfiguration1OrderConfigurationAnyOf3
    | LimitLimitGtdConfiguration1OrderConfigurationAnyOf4
    | LimitLimitFokConfiguration1OrderConfigurationAnyOf5
    | TwapLimitGtdConfiguration1OrderConfigurationAnyOf6
    | StopLimitStopLimitGtcConfiguration1OrderConfigurationAnyOf7
    | StopLimitStopLimitGtdConfiguration1OrderConfigurationAnyOf8
    | TriggerBracketGtcConfiguration1OrderConfigurationAnyOf9
    | TriggerBracketGtdConfiguration1OrderConfigurationAnyOf10
    | ScaledLimitGtcConfiguration1OrderConfigurationAnyOf11
  ]
  """Configuration of the attempted closing order."""


class ClosePositionSuccess(TypedDict):
  success: bool
  """Whether the closing order was created."""
  success_response: NewOrderSuccessResponse
  order_configuration: NotRequired[
    MarketMarketIocConfiguration0OrderConfigurationAnyOf0
    | MarketMarketFokConfiguration0OrderConfigurationAnyOf1
    | SorLimitIocConfiguration0OrderConfigurationAnyOf2
    | LimitLimitGtcConfiguration0OrderConfigurationAnyOf3
    | LimitLimitGtdConfiguration0OrderConfigurationAnyOf4
    | LimitLimitFokConfiguration0OrderConfigurationAnyOf5
    | TwapLimitGtdConfiguration0OrderConfigurationAnyOf6
    | StopLimitStopLimitGtcConfiguration0OrderConfigurationAnyOf7
    | StopLimitStopLimitGtdConfiguration0OrderConfigurationAnyOf8
    | TriggerBracketGtcConfiguration0OrderConfigurationAnyOf9
    | TriggerBracketGtdConfiguration0OrderConfigurationAnyOf10
    | ScaledLimitGtcConfiguration0OrderConfigurationAnyOf11
  ]
  """Configuration of the generated closing order."""


_Type = ClosePositionSuccess | ClosePositionFailure
adapter = validator[_Type](_Type)  # type: ignore


@dataclass(frozen=True, kw_only=True)
class ClosePosition(RpcEndpoint):
  """`POST /api/v3/brokerage/orders/close_position`."""

  async def __call__(
    self,
    *,
    client_order_id: str,
    product_id: str,
    size: str | None = None,
  ) -> ClosePositionSuccess | ClosePositionFailure:
    """Place a market order to close an open futures/perpetuals position, in full or in part.

    Args:
      client_order_id: A caller-supplied unique id for the closing order.
      product_id: The contract's product id, e.g. `BIT-28JUL23-CDE`.
      size: Number of contracts to close; omit to close the full position.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/orders/close-position)
    """
    body: dict = {
      'client_order_id': client_order_id,
      'product_id': product_id,
    }
    if size is not None:
      body['size'] = size
    return await self.authed_request(
      'POST', '/api/v3/brokerage/orders/close_position', json=body, validator=adapter
    )
