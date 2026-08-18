"""`incremental_ticker.{instrument_name}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class BookStats(TypedDict):
  """24h trading statistics."""

  volume: float
  """Volume during the last 24h, in base currency."""
  low: float
  """Lowest price during the last 24h."""
  high: float
  """Highest price during the last 24h."""
  price_change: NotRequired[float]
  """24-hour price change, expressed as a percentage; absent if there weren't any trades."""
  volume_usd: NotRequired[float]
  """Volume in USD (futures only)."""
  volume_notional: NotRequired[float]
  """Volume in quote currency (futures and spot only). Observed live; not documented in the venue AsyncAPI schema."""


class Greeks(TypedDict):
  """Option Greeks (options only)."""

  delta: float
  """Black-Scholes delta for the option."""
  gamma: float
  """Gamma for the option."""
  rho: float
  """Rho for the option."""
  theta: float
  """Theta for the option (minimum of 1-day theta and lifetime theta)."""
  vega: float
  """Vega for the option."""


class IncrementalTickerUpdate(TypedDict):
  """Real-time ticker update for an instrument: the first push is a full snapshot, later pushes carry only the fields that changed since the previous update."""

  type: NotRequired[Literal['snapshot', 'change']]
  """`snapshot` for the first notification, `change` for every later one."""
  instrument_name: str
  """Unique instrument identifier."""
  timestamp: int
  """The timestamp (milliseconds since the Unix epoch)."""
  state: NotRequired[
    Literal[
      'open', 'settlement', 'delivered', 'inactive', 'locked', 'halted', 'archivized'
    ]
  ]
  """The state of the order book, i.e. the instrument's current lifecycle stage: `open` (live trading), `settlement` (settlement/delivery in progress), `delivered` (delivered, final), `inactive` (deactivated), `locked` (only cancels accepted), `halted` (error state), `archivized` (moved to expired instruments, final)."""
  stats: NotRequired[BookStats]
  open_interest: NotRequired[float]
  """Total outstanding contracts, in the corresponding amount units (USD for perpetual/inverse futures, underlying coin for options/linear futures)."""
  best_bid_price: NotRequired[float]
  """The current best bid price; absent if there aren't any bids."""
  best_bid_amount: NotRequired[float]
  """Requested order size of all best bids."""
  best_ask_price: NotRequired[float]
  """The current best ask price; absent if there aren't any asks."""
  best_ask_amount: NotRequired[float]
  """Requested order size of all best asks."""
  index_price: NotRequired[float]
  """Current index price."""
  min_price: NotRequired[float]
  """The minimum price for the instrument; sell orders below this are clamped up to it."""
  max_price: NotRequired[float]
  """The maximum price for the instrument; buy orders above this are clamped down to it."""
  mark_price: NotRequired[float]
  """The mark price for the instrument."""
  last_price: NotRequired[float]
  """The price for the last trade."""
  underlying_price: NotRequired[float]
  """Underlying price for implied-volatility calculations (options only)."""
  underlying_index: NotRequired[float]
  """Name of the underlying future, or `index_price` (options only). Documented as a number by the venue despite naming an index."""
  interest_rate: NotRequired[float]
  """Interest rate used in implied-volatility calculations (options only)."""
  bid_iv: NotRequired[float]
  """Implied volatility for the best bid (options only)."""
  ask_iv: NotRequired[float]
  """Implied volatility for the best ask (options only)."""
  mark_iv: NotRequired[float]
  """Implied volatility for the mark price (options only)."""
  greeks: NotRequired[Greeks]
  funding_8h: NotRequired[float]
  """8-hour funding rate (perpetual only)."""
  current_funding: NotRequired[float]
  """Current funding rate (perpetual only)."""
  interest_value: NotRequired[float]
  """Value used to calculate `realized_funding` in positions (perpetual only)."""
  delivery_price: NotRequired[float]
  """The settlement price for the instrument. Only present when `state` is a delivered/settled state."""
  settlement_price: NotRequired[float]
  """The settlement price for the instrument. Only present while `state` is `open`; absent for spot."""
  estimated_delivery_price: NotRequired[float]
  """Estimated delivery price for the market."""


validate_incremental_ticker = validator[IncrementalTickerUpdate](
  IncrementalTickerUpdate
)


class IncrementalTicker(StreamEndpoint):
  """`incremental_ticker.{instrument_name}` subscription."""

  def incremental_ticker(
    self,
    instrument_name: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[IncrementalTickerUpdate, Any, Any]:
    """Real-time ticker updates for an instrument, delivered as a full snapshot followed by incremental updates carrying only the fields that changed. Sent at most once per second.

    Args:
      instrument_name: The name of the instrument.
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/market-data/incremental_tickerinstrument_name)
    """
    channel = f'incremental_ticker.{instrument_name}'
    return self.subscribe(
      channel, validator=validate_incremental_ticker, validate=validate
    )
