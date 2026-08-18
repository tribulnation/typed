from dataclasses import dataclass
from typed_core.util import StreamManager
from typing_extensions import Any, Literal, TypedDict
from typed_core.validation import validator
from coinbase.core.endpoint.stream import StreamEndpoint


class FcmMarginWindowMeasureIntradayMarginWindowMeasureAnyOf0(TypedDict):
  """Margin figures for the intraday margin window."""

  margin_window_type: Literal[
    'FCM_MARGIN_WINDOW_TYPE_UNSPECIFIED',
    'FCM_MARGIN_WINDOW_TYPE_OVERNIGHT',
    'FCM_MARGIN_WINDOW_TYPE_WEEKEND',
    'FCM_MARGIN_WINDOW_TYPE_INTRADAY',
    'FCM_MARGIN_WINDOW_TYPE_TRANSITION',
  ]
  """Which margin window this measure describes."""
  margin_level: Literal[
    'MARGIN_LEVEL_TYPE_UNSPECIFIED',
    'MARGIN_LEVEL_TYPE_BASE',
    'MARGIN_LEVEL_TYPE_WARNING',
    'MARGIN_LEVEL_TYPE_DANGER',
    'MARGIN_LEVEL_TYPE_LIQUIDATION',
  ]
  """Current margin status for this window."""
  initial_margin: str
  """Initial margin required for this window."""
  maintenance_margin: str
  """Maintenance margin required for this window."""
  liquidation_buffer_percentage: str
  """Liquidation buffer for this window, expressed as a percentage."""
  total_hold: str
  """Total balance on hold for this window."""
  futures_buying_power: str
  """Futures buying power for this window."""


class FcmMarginWindowMeasureOvernightMarginWindowMeasureAnyOf0(TypedDict):
  """Margin figures for the overnight margin window."""

  margin_window_type: Literal[
    'FCM_MARGIN_WINDOW_TYPE_UNSPECIFIED',
    'FCM_MARGIN_WINDOW_TYPE_OVERNIGHT',
    'FCM_MARGIN_WINDOW_TYPE_WEEKEND',
    'FCM_MARGIN_WINDOW_TYPE_INTRADAY',
    'FCM_MARGIN_WINDOW_TYPE_TRANSITION',
  ]
  """Which margin window this measure describes."""
  margin_level: Literal[
    'MARGIN_LEVEL_TYPE_UNSPECIFIED',
    'MARGIN_LEVEL_TYPE_BASE',
    'MARGIN_LEVEL_TYPE_WARNING',
    'MARGIN_LEVEL_TYPE_DANGER',
    'MARGIN_LEVEL_TYPE_LIQUIDATION',
  ]
  """Current margin status for this window."""
  initial_margin: str
  """Initial margin required for this window."""
  maintenance_margin: str
  """Maintenance margin required for this window."""
  liquidation_buffer_percentage: str
  """Liquidation buffer for this window, expressed as a percentage."""
  total_hold: str
  """Total balance on hold for this window."""
  futures_buying_power: str
  """Futures buying power for this window."""


class FuturesBalanceSummaryParams(TypedDict):
  """Empty: `futures_balance_summary` takes no subscribe parameters beyond `type`/`channel`/`jwt`."""


class FuturesBalanceSummarySubscriptionEvent(TypedDict):
  """Snapshot of every channel currently subscribed on this connection."""

  subscriptions: dict[str, list[str]]
  """Map of channel name to the subscription's scoping ids. Verified live: for this channel it is not empty despite the channel taking no product scoping -- it carries the key's portfolio id."""


class FcmBalanceSummary(TypedDict):
  """The key's CFM futures balance, margin, and liquidation figures."""

  futures_buying_power: str
  """Amount of the cash balance available to trade CFM futures."""
  total_usd_balance: str
  """Aggregate USD balance across the CFTC-regulated futures account and the Coinbase Inc. spot account."""
  cbi_usd_balance: str
  """USD balance held in the Coinbase Inc. spot account."""
  cfm_usd_balance: str
  """USD balance held in the CFTC-regulated futures account."""
  total_open_orders_hold_amount: str
  """Total balance on hold for spot and futures open orders."""
  unrealized_pnl: str
  """Current unrealized profit/loss across all open futures positions."""
  daily_realized_pnl: str
  """Realized gains/losses from the current trade date."""
  initial_margin: str
  """Margin required to initiate the key's current futures positions."""
  available_margin: str
  """Funds available to meet margin requirements."""
  liquidation_threshold: str
  """Account value at which positions begin to be liquidated."""
  liquidation_buffer_amount: str
  """Funds available in excess of the liquidation threshold."""
  liquidation_buffer_percentage: str
  """Liquidation buffer, expressed as a percentage."""
  intraday_margin_window_measure: (
    FcmMarginWindowMeasureIntradayMarginWindowMeasureAnyOf0 | None
  )
  """Margin figures for the intraday margin window. Verified live: `null` when the key has no futures margin activity to report."""
  overnight_margin_window_measure: (
    FcmMarginWindowMeasureOvernightMarginWindowMeasureAnyOf0 | None
  )
  """Margin figures for the overnight margin window. Verified live: `null` when the key has no futures margin activity to report."""


class FuturesBalanceSummarySubscribeAck(TypedDict):
  """Confirms the channel is now (un)subscribed."""

  channel: Literal['subscriptions']
  """Always `subscriptions` for an acknowledgement frame."""
  timestamp: str
  """Server timestamp the acknowledgement was generated, RFC 3339."""
  sequence_num: int
  """Per-connection sequence number of this frame."""
  events: list[FuturesBalanceSummarySubscriptionEvent]
  """Always one event describing the connection's current subscriptions."""


class FuturesBalanceSummaryEvent(TypedDict):
  """One futures balance summary snapshot."""

  type: str
  """Event kind; only `snapshot` is documented on the source page."""
  fcm_balance_summary: FcmBalanceSummary


class FuturesBalanceSummaryMessage(TypedDict):
  """The whole frame the caller receives: the client core does not unwrap `events`."""

  channel: Literal['futures_balance_summary']
  """Always `futures_balance_summary`."""
  timestamp: str
  """Server timestamp the message was generated, RFC 3339."""
  sequence_num: int
  """Monotonically increasing per-connection sequence number, used to detect dropped messages."""
  events: list[FuturesBalanceSummaryEvent]
  """Always one balance-summary event per message."""


@dataclass(frozen=True, kw_only=True)
class FuturesBalanceSummary(StreamEndpoint):
  """`futures_balance_summary` channel."""

  def __call__(self) -> StreamManager[FuturesBalanceSummaryMessage, Any, Any]:
    """Real-time CFM futures balance and margin summary for the key's portfolio. Authenticated: subscribed via `authed_subscribe`, embedding a fresh JWT in the subscribe message. Takes no product scoping.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-channels)
    """
    return self.authed_subscribe(
      'futures_balance_summary', None, validator=validator(FuturesBalanceSummaryMessage)
    )
