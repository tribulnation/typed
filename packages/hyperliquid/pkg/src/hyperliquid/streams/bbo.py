from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class BboLevel0(TypedDict):
  """Best bid level."""

  n: int
  """Number of individual orders resting at this price level."""
  px: str
  """Price of this level."""
  sz: str
  """Total size resting at this price level."""


class BboLevel1(TypedDict):
  """Best ask level."""

  n: int
  """Number of individual orders resting at this price level."""
  px: str
  """Price of this level."""
  sz: str
  """Total size resting at this price level."""


class BboParams(TypedDict):
  """Subscription parameters for the `bbo` channel."""

  coin: str
  """Coin symbol to subscribe to, e.g. `BTC`."""


class BboSubscription(TypedDict):
  """Subscription parameters that were acknowledged."""

  coin: str
  """Coin symbol the acknowledged subscription covers."""
  type: Literal['bbo']
  """Subscription channel identifier."""


class SubscribeAck(TypedDict):
  """Echo of the subscription that was acknowledged."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: BboSubscription


class WsBbo(TypedDict):
  """Pushed best-bid/offer update for one coin."""

  bbo: tuple[BboLevel0, BboLevel1]
  """Best bid and ask, as [bid, ask]."""
  coin: str
  """Coin symbol this update is for."""
  time: int
  """Update timestamp, epoch milliseconds."""


adapter = pydantic.TypeAdapter(WsBbo)


class Bbo(StreamsMixin):
  def bbo(self, coin: str):
    """Subscribe to Hyperliquid `bbo` updates: the best bid and ask level for one coin.

    Args:
      coin: Coin symbol to subscribe to, e.g. `BTC`.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._bbo_impl(coin))

  async def _bbo_impl(self, coin: str):
    params: dict[str, object] = {
      'coin': coin,
    }
    stream = await self.subscribe(
      f'bbo:{coin.lower()}',
      params,
      request_channel='bbo',
      message_key=lambda data: f'bbo:{data["coin"].lower()}',
    )

    def match(msg):
      return msg.get('coin', '').lower() == coin.lower()

    stream = stream.filter(match)

    def mapper(msg) -> WsBbo:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
