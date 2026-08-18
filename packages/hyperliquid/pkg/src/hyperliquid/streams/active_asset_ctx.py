from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class ActiveAssetCtxParams(TypedDict):
  """Subscription parameters for the `activeAssetCtx` channel."""

  coin: str
  """Coin symbol to subscribe to, e.g. `BTC`."""


class ActiveAssetCtxSubscription(TypedDict):
  """Subscription parameters that were acknowledged."""

  coin: str
  """Coin symbol the acknowledged subscription covers."""
  type: Literal['activeAssetCtx']
  """Subscription channel identifier."""


class PerpsAssetCtx(TypedDict):
  """Perp market context: prices, funding, and volume for one coin."""

  dayNtlVlm: str
  """24-hour trading volume in notional (quote-currency) terms."""
  prevDayPx: str
  """Mark price 24 hours ago."""
  markPx: str
  """Current mark price."""
  midPx: str | None
  """Current mid price between best bid and ask; null when the book has no two-sided market."""
  funding: str
  """Current hourly funding rate."""
  openInterest: str
  """Total open interest in base-asset units."""
  oraclePx: str
  """Current oracle price."""
  premium: str | None
  """Premium of mark price over oracle price; null when it cannot be computed."""
  dayBaseVlm: str
  """24-hour trading volume in base-asset units."""
  impactPxs: NotRequired[tuple[str, str] | None]
  """Impact bid/ask prices used to estimate slippage, as [bid, ask]; absent or null when unavailable."""


class SpotAssetCtx(TypedDict):
  """Spot market context: prices, volume, and circulating supply for one token."""

  dayNtlVlm: str
  """24-hour trading volume in notional (quote-currency) terms."""
  prevDayPx: str
  """Mark price 24 hours ago."""
  markPx: str
  """Current mark price."""
  midPx: str | None
  """Current mid price between best bid and ask; null when the book has no two-sided market."""
  circulatingSupply: str
  """Circulating supply of the spot token."""


class SubscribeAck(TypedDict):
  """Echo of the subscription that was acknowledged."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: ActiveAssetCtxSubscription


class WsActiveAssetCtx(TypedDict):
  """Active asset context for a perp coin."""

  coin: str
  """Coin symbol this context is for."""
  ctx: PerpsAssetCtx


class WsActiveSpotAssetCtx(TypedDict):
  """Active asset context for a spot coin. Documented by upstream (`WsActiveSpotAssetCtx`) but never observed in a live capture -- every recorded example subscribes to a perp coin."""

  coin: str
  """Coin symbol this context is for."""
  ctx: SpotAssetCtx


adapter = pydantic.TypeAdapter(WsActiveAssetCtx | WsActiveSpotAssetCtx)


class ActiveAssetCtx(StreamsMixin):
  def active_asset_ctx(self, coin: str):
    """Subscribe to Hyperliquid `activeAssetCtx` updates: the live market context (prices, funding, volume) for one coin.

    Args:
      coin: Coin symbol to subscribe to, e.g. `BTC`.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._active_asset_ctx_impl(coin))

  async def _active_asset_ctx_impl(self, coin: str):
    params: dict[str, object] = {
      'coin': coin,
    }
    stream = await self.subscribe(
      f'activeAssetCtx:{coin.lower()}',
      params,
      request_channel='activeAssetCtx',
      message_key=lambda data: f'activeAssetCtx:{data["coin"].lower()}',
    )

    def match(msg):
      return msg.get('coin', '').lower() == coin.lower()

    stream = stream.filter(match)

    def mapper(msg) -> WsActiveAssetCtx | WsActiveSpotAssetCtx:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
