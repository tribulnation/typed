"""`ticker.{instrument_name}.{interval}` — subscription."""

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


class Ticker(TypedDict):
  """A snapshot of one instrument's order book and market statistics, pushed on every interval tick."""

  instrument_name: str
  """Unique instrument identifier."""
  timestamp: int
  """The timestamp (milliseconds since the Unix epoch)."""
  state: Literal[
    'open', 'settlement', 'delivered', 'inactive', 'locked', 'halted', 'archivized'
  ]
  """The state of the order book, i.e. the instrument's current lifecycle stage: `open` (live trading), `settlement` (settlement/delivery in progress), `delivered` (delivered, final), `inactive` (deactivated), `locked` (only cancels accepted), `halted` (error state), `archivized` (moved to expired instruments, final)."""
  stats: BookStats
  open_interest: float
  """Total outstanding contracts, in the corresponding amount units (USD for perpetual/inverse futures, underlying coin for options/linear futures)."""
  best_bid_price: float | None
  """The current best bid price; absent if there aren't any bids."""
  best_bid_amount: float | None
  """Requested order size of all best bids."""
  best_ask_price: float | None
  """The current best ask price; absent if there aren't any asks."""
  best_ask_amount: float | None
  """Requested order size of all best asks."""
  index_price: float
  """Current index price."""
  min_price: float
  """The minimum price for the instrument; sell orders below this are clamped up to it."""
  max_price: float
  """The maximum price for the instrument; buy orders above this are clamped down to it."""
  mark_price: float
  """The mark price for the instrument."""
  last_price: float | None
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
  estimated_delivery_price: float
  """Estimated delivery price for the market."""
  is_anchor_breached: NotRequired[bool]
  """Whether the mark price has breached the anchor price band. Only present for RWA perpetual instruments when an anchor price is active."""
  anchor_min_price: NotRequired[float]
  """The lower bound of the anchor price band, computed as `anchor_price * (1 - bandwidth)`. Only present for RWA perpetual instruments when an anchor price and bandwidth are defined."""
  anchor_max_price: NotRequired[float]
  """The upper bound of the anchor price band, computed as `anchor_price * (1 + bandwidth)`. Only present for RWA perpetual instruments when an anchor price and bandwidth are defined."""


validate_ticker = validator[Ticker](Ticker)


class TickerEndpoint(StreamEndpoint):
  """`ticker.{instrument_name}.{interval}` subscription."""

  def ticker(
    self,
    instrument_name: str,
    interval: Literal['raw', '100ms', 'agg2'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[Ticker, Any, Any]:
    """Real-time ticker data providing comprehensive market information for the specified instrument: best bid/ask, last/mark/index price, 24h stats, open interest, and (where applicable) option Greeks/IV or perpetual funding. `interval` controls the push cadence: `raw` (no aggregation, authorized users only), `100ms`, or `agg2`.

    Args:
      instrument_name: The name of the instrument.
      interval: Frequency of notifications; events are aggregated over this interval. `raw` means no aggregation and is only available to authorized users.
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/market-data/tickerinstrument_nameinterval)
    """
    channel = f'ticker.{instrument_name}.{interval}'
    return self.subscribe(channel, validator=validate_ticker, validate=validate)
