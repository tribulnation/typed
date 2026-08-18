from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class Trade(TypedDict):
  """One executed trade print."""

  coin: str
  """Coin symbol traded."""
  side: Literal['A', 'B']
  """Aggressor side code: A (ask/sell) or B (bid/buy)."""
  px: str
  """Trade price."""
  sz: str
  """Trade size."""
  hash: str
  """L1 transaction hash."""
  time: int
  """Trade timestamp in epoch milliseconds."""
  tid: int
  """Unique trade id -- a 50-bit hash of the buyer and seller order ids. Combine with block time and coin for a globally unique id."""
  users: tuple[str, str]
  """The two counterparty addresses, as [buyer, seller]."""


class TradesSubscription(TypedDict):
  """Subscription parameters that were acknowledged."""

  coin: str
  """Coin symbol subscribed to."""
  type: Literal['trades']
  """Subscription channel identifier."""


class TradesSubscriptionParams(TypedDict):
  """Subscription parameters for the `trades` channel."""

  coin: str
  """Coin symbol to subscribe to trade prints for."""


class TradesSubscribeAck(TypedDict):
  """Echo of the subscription that was acknowledged."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: TradesSubscription


adapter = pydantic.TypeAdapter(list[Trade])


class Trades(StreamsMixin):
  def trades(self, coin: str):
    """Subscribe to Hyperliquid `trades` updates.

    Args:
      coin: Coin symbol to subscribe to trade prints for.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._trades_impl(coin))

  async def _trades_impl(self, coin: str):
    params: dict[str, object] = {
      'coin': coin,
    }
    stream = await self.subscribe(
      f'trades:{coin.lower()}',
      params,
      request_channel='trades',
      message_key=lambda data: f'trades:{data[0]["coin"].lower()}',
    )

    def match(msg):
      if not msg or not isinstance(msg[0], dict):
        return False
      return msg[0].get('coin', '').lower() == coin.lower()

    stream = stream.filter(match)

    def mapper(msg) -> list[Trade]:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
