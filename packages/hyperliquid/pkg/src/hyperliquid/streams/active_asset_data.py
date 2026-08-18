from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class ActiveAssetDataParams(TypedDict):
  """Subscription parameters for the `activeAssetData` channel."""

  coin: str
  """Coin symbol to subscribe to, e.g. `BTC`."""
  user: str
  """Wallet address to subscribe to."""


class ActiveAssetDataSubscription(TypedDict):
  """Subscription parameters that were acknowledged."""

  coin: str
  """Coin symbol the acknowledged subscription covers."""
  type: Literal['activeAssetData']
  """Subscription channel identifier."""
  user: str
  """Wallet address the acknowledged subscription is scoped to."""


class Leverage(TypedDict):
  """User's current leverage setting for this coin."""

  type: Literal['cross', 'isolated']
  """Margin mode this leverage setting applies under."""
  value: int
  """Leverage multiplier."""


class SubscribeAck(TypedDict):
  """Echo of the subscription that was acknowledged."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: ActiveAssetDataSubscription


class WsActiveAssetData(TypedDict):
  """Pushed update of one user's leverage and tradable size for one perp coin."""

  availableToTrade: tuple[str, str]
  """Remaining tradable size, as [long, short]."""
  coin: str
  """Coin symbol this data is for."""
  leverage: Leverage
  markPx: str
  """Current mark price."""
  maxTradeSzs: tuple[str, str]
  """Maximum order size at current leverage, as [long, short]."""
  user: str
  """Wallet address this data is for."""


adapter = pydantic.TypeAdapter(WsActiveAssetData)


class ActiveAssetData(StreamsMixin):
  def active_asset_data(self, coin: str, user: str):
    """Subscribe to Hyperliquid `activeAssetData` updates: one user's leverage and tradable size for one perp coin. Perps only.

    Args:
      coin: Coin symbol to subscribe to, e.g. `BTC`.
      user: Wallet address to subscribe to.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._active_asset_data_impl(coin, user))

  async def _active_asset_data_impl(self, coin: str, user: str):
    params: dict[str, object] = {
      'coin': coin,
      'user': user,
    }
    stream = await self.subscribe(
      f'activeAssetData:{user.lower()}:{coin.lower()}',
      params,
      request_channel='activeAssetData',
      message_key=lambda data: (
        f'activeAssetData:{data["user"].lower()}:{data["coin"].lower()}'
      ),
    )

    def match(msg):
      return (
        msg.get('user', '').lower() == user.lower()
        and msg.get('coin', '').lower() == coin.lower()
      )

    stream = stream.filter(match)

    def mapper(msg) -> WsActiveAssetData:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
