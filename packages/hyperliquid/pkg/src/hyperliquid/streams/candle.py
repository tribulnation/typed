from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class Candle(TypedDict):
  """Pushed candle update for the subscribed coin and interval."""

  T: int
  """Candle close time, as a millisecond epoch timestamp."""
  c: str
  """Close price."""
  h: str
  """High price."""
  i: Literal[
    '1m',
    '3m',
    '5m',
    '15m',
    '30m',
    '1h',
    '2h',
    '4h',
    '8h',
    '12h',
    '1d',
    '3d',
    '1w',
    '1M',
  ]
  """Candle interval."""
  l: str
  """Low price."""
  n: int
  """Number of trades that occurred during this candle."""
  o: str
  """Open price."""
  s: str
  """Coin symbol this candle is for."""
  t: int
  """Candle open time, as a millisecond epoch timestamp."""
  v: str
  """Trading volume during this candle, in base-asset units."""


class CandleSubscriptionEcho(TypedDict):
  """Echo of the candle subscription that was acknowledged."""

  coin: str
  """Coin symbol the subscription is for."""
  interval: Literal[
    '1m',
    '3m',
    '5m',
    '15m',
    '30m',
    '1h',
    '2h',
    '4h',
    '8h',
    '12h',
    '1d',
    '3d',
    '1w',
    '1M',
  ]
  """Candle interval the subscription is for."""
  type: Literal['candle']
  """Subscription channel identifier."""


class CandleSubscriptionParams(TypedDict):
  """Candle subscription parameters: coin symbol and interval."""

  coin: str
  """Coin symbol to subscribe to candles for."""
  interval: Literal[
    '1m',
    '3m',
    '5m',
    '15m',
    '30m',
    '1h',
    '2h',
    '4h',
    '8h',
    '12h',
    '1d',
    '3d',
    '1w',
    '1M',
  ]
  """Candle interval to subscribe to."""


class CandleSubscribeAck(TypedDict):
  """Acknowledgement of a candle subscribe/unsubscribe request."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: CandleSubscriptionEcho


adapter = pydantic.TypeAdapter(Candle)


class CandleEndpoint(StreamsMixin):
  def candle(
    self,
    coin: str,
    interval: Literal[
      '1m',
      '3m',
      '5m',
      '15m',
      '30m',
      '1h',
      '2h',
      '4h',
      '8h',
      '12h',
      '1d',
      '3d',
      '1w',
      '1M',
    ],
  ):
    """Subscribe to Hyperliquid `candle` updates.

    Args:
      coin: Coin symbol to subscribe to candles for.
      interval: Candle interval to subscribe to.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._candle_impl(coin, interval))

  async def _candle_impl(
    self,
    coin: str,
    interval: Literal[
      '1m',
      '3m',
      '5m',
      '15m',
      '30m',
      '1h',
      '2h',
      '4h',
      '8h',
      '12h',
      '1d',
      '3d',
      '1w',
      '1M',
    ],
  ):
    params: dict[str, object] = {
      'coin': coin,
      'interval': interval,
    }
    stream = await self.subscribe(
      f'candle:{coin.lower()}:{interval.lower()}',
      params,
      request_channel='candle',
      message_key=lambda data: f'candle:{data["s"].lower()}:{data["i"].lower()}',
    )

    def match(msg):
      return (
        msg.get('s', '').lower() == coin.lower()
        and msg.get('i', '').lower() == interval.lower()
      )

    stream = stream.filter(match)

    def mapper(msg) -> Candle:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
