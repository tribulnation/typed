from dataclasses import dataclass
from typed_core.util import StreamManager
from typing_extensions import Any, Literal, TypedDict
from typed_core.validation import validator
from coinbase.core.endpoint.stream import StreamEndpoint


class CandleUpdate(TypedDict):
  """One product's 5-minute candle."""

  start: str
  """UNIX timestamp (seconds, as a string) marking the start of the candle interval."""
  high: str
  """Highest trade price during the interval."""
  low: str
  """Lowest trade price during the interval."""
  open: str
  """First trade price during the interval."""
  close: str
  """Last trade price during the interval."""
  volume: str
  """Base-currency amount traded during the interval."""
  product_id: str
  """Product this candle belongs to."""


class CandlesParams(TypedDict):
  """Products to receive candle updates for."""

  product_ids: list[str]
  """Product ids to stream, e.g. `["BTC-USD"]`."""


class CandlesSubscriptionEvent(TypedDict):
  """Snapshot of every channel currently subscribed on this connection."""

  subscriptions: dict[str, list[str]]
  """Map of channel name to the product ids subscribed on it."""


class CandlesEvent(TypedDict):
  """One batch of candle updates."""

  type: str
  """Event kind; only `snapshot` is documented on the source page."""
  candles: list[CandleUpdate]
  """Updated candles."""


class CandlesSubscribeAck(TypedDict):
  """Confirms the channel is now (un)subscribed."""

  channel: Literal['subscriptions']
  """Always `subscriptions` for an acknowledgement frame."""
  timestamp: str
  """Server timestamp the acknowledgement was generated, RFC 3339."""
  sequence_num: int
  """Per-connection sequence number of this frame."""
  events: list[CandlesSubscriptionEvent]
  """Always one event describing the connection's current subscriptions."""


class CandlesMessage(TypedDict):
  """The whole frame the caller receives: the client core does not unwrap `events`."""

  channel: Literal['candles']
  """Always `candles`."""
  timestamp: str
  """Server timestamp the message was generated, RFC 3339."""
  sequence_num: int
  """Monotonically increasing per-connection sequence number, used to detect dropped messages."""
  events: list[CandlesEvent]
  """One or more candle-batch events."""


@dataclass(frozen=True, kw_only=True)
class Candles(StreamEndpoint):
  """`candles` channel."""

  def __call__(self, product_ids: list[str]) -> StreamManager[CandlesMessage, Any, Any]:
    """Real-time 5-minute-bucket candle updates for the given products. No authentication required.

    Args:
      product_ids: Product ids to stream, e.g. `["BTC-USD"]`.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-channels)
    """
    params: dict = {
      'product_ids': product_ids,
    }
    return self.subscribe('candles', params, validator=validator(CandlesMessage))
