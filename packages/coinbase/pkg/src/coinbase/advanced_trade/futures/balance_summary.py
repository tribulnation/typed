from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class AmountAvailableMargin(TypedDict):
  """Margin available beyond what is currently required."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountCbiUsdBalance(TypedDict):
  """USD balance held in the Coinbase (spot) wallet."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountCfmUsdBalance(TypedDict):
  """USD balance held in the CFM futures wallet."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountDailyRealizedPnl(TypedDict):
  """Realized profit and loss from trades on the current trade date."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountFundingPnl(TypedDict):
  """Profit and loss from futures funding payments."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountFuturesBuyingPower(TypedDict):
  """Buying power available for futures trading."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountInitialMargin(TypedDict):
  """Initial margin currently required."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountLiquidationBufferAmount(TypedDict):
  """Buffer amount above the liquidation threshold."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountLiquidationThreshold(TypedDict):
  """Balance threshold below which positions may be liquidated."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountTotalOpenOrdersHoldAmount(TypedDict):
  """Amount held against open futures orders."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountTotalPendingTransfersAmount(TypedDict):
  """Amount pending transfer between the futures and spot wallets."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountTotalUsdBalance(TypedDict):
  """Total USD balance across the futures and spot wallets."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountUnrealizedPnl(TypedDict):
  """Unrealized profit and loss across open futures positions."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class FcmMarginWindowMeasureIntradayMarginWindowMeasure(TypedDict):
  """Margin measures for the current intraday window."""

  margin_window_type: Literal[
    'FCM_MARGIN_WINDOW_TYPE_UNSPECIFIED',
    'FCM_MARGIN_WINDOW_TYPE_OVERNIGHT',
    'FCM_MARGIN_WINDOW_TYPE_WEEKEND',
    'FCM_MARGIN_WINDOW_TYPE_INTRADAY',
    'FCM_MARGIN_WINDOW_TYPE_TRANSITION',
  ]
  """Which margin window this measures."""
  margin_level: Literal[
    'MARGIN_LEVEL_TYPE_UNSPECIFIED',
    'MARGIN_LEVEL_TYPE_BASE',
    'MARGIN_LEVEL_TYPE_WARNING',
    'MARGIN_LEVEL_TYPE_DANGER',
    'MARGIN_LEVEL_TYPE_LIQUIDATION',
  ]
  """Current margin severity level for this window."""
  initial_margin: str
  """Initial margin required for this window."""
  maintenance_margin: str
  """Maintenance margin required for this window."""
  liquidation_buffer: str
  """Buffer above the liquidation threshold for this window."""
  total_hold: str
  """Total amount held for this window."""
  futures_buying_power: str
  """Futures buying power available for this window."""


class FcmMarginWindowMeasureOvernightMarginWindowMeasure(TypedDict):
  """Margin measures for the current overnight window."""

  margin_window_type: Literal[
    'FCM_MARGIN_WINDOW_TYPE_UNSPECIFIED',
    'FCM_MARGIN_WINDOW_TYPE_OVERNIGHT',
    'FCM_MARGIN_WINDOW_TYPE_WEEKEND',
    'FCM_MARGIN_WINDOW_TYPE_INTRADAY',
    'FCM_MARGIN_WINDOW_TYPE_TRANSITION',
  ]
  """Which margin window this measures."""
  margin_level: Literal[
    'MARGIN_LEVEL_TYPE_UNSPECIFIED',
    'MARGIN_LEVEL_TYPE_BASE',
    'MARGIN_LEVEL_TYPE_WARNING',
    'MARGIN_LEVEL_TYPE_DANGER',
    'MARGIN_LEVEL_TYPE_LIQUIDATION',
  ]
  """Current margin severity level for this window."""
  initial_margin: str
  """Initial margin required for this window."""
  maintenance_margin: str
  """Maintenance margin required for this window."""
  liquidation_buffer: str
  """Buffer above the liquidation threshold for this window."""
  total_hold: str
  """Total amount held for this window."""
  futures_buying_power: str
  """Futures buying power available for this window."""


class FcmBalanceSummary(TypedDict):
  """Balances and margin state for the futures wallet."""

  futures_buying_power: AmountFuturesBuyingPower
  total_usd_balance: AmountTotalUsdBalance
  cbi_usd_balance: AmountCbiUsdBalance
  cfm_usd_balance: AmountCfmUsdBalance
  total_open_orders_hold_amount: AmountTotalOpenOrdersHoldAmount
  unrealized_pnl: AmountUnrealizedPnl
  daily_realized_pnl: AmountDailyRealizedPnl
  initial_margin: AmountInitialMargin
  available_margin: AmountAvailableMargin
  liquidation_threshold: AmountLiquidationThreshold
  liquidation_buffer_amount: AmountLiquidationBufferAmount
  liquidation_buffer_percentage: str
  """Buffer above the liquidation threshold, as a percentage."""
  intraday_margin_window_measure: FcmMarginWindowMeasureIntradayMarginWindowMeasure
  overnight_margin_window_measure: FcmMarginWindowMeasureOvernightMarginWindowMeasure
  total_pending_transfers_amount: AmountTotalPendingTransfersAmount
  funding_pnl: AmountFundingPnl


class GetFuturesBalanceSummaryResponse(TypedDict):
  """Futures balance summary response."""

  balance_summary: FcmBalanceSummary


@dataclass(frozen=True, kw_only=True)
class BalanceSummary(RpcEndpoint):
  """`GET /api/v3/brokerage/cfm/balance_summary`."""

  async def __call__(self) -> GetFuturesBalanceSummaryResponse:
    """Get a summary of balances for the CFM (Coinbase Financial Markets) futures wallet.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/futures/get-futures-balance-summary)
    """
    return await self.authed_request(
      'GET',
      '/api/v3/brokerage/cfm/balance_summary',
      validator=validator(GetFuturesBalanceSummaryResponse),
    )
