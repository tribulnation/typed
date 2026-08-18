from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class Body(TypedDict):
  """No parameters; subscribes to the compressed mark/mid price feed across every asset."""


class FastAssetCtxsSubscriptionEcho(TypedDict):
  """Echo of the subscription that was acknowledged."""

  type: Literal['fastAssetCtxs']
  """Subscription channel identifier."""


class FastAssetCtxsSubscribeAck(TypedDict):
  """Acknowledgement of a fastAssetCtxs subscribe/unsubscribe request."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: FastAssetCtxsSubscriptionEcho


adapter = pydantic.TypeAdapter(str)


class FastAssetCtxs(StreamsMixin):
  def fast_asset_ctxs(self):
    """Subscribe to Hyperliquid `fastAssetCtxs` updates: a low-latency mark/mid price feed across every asset on the venue, pushed as a base64-encoded, raw-DEFLATE-compressed JSON payload rather than plain JSON. See this endpoint's `notes` for the full decode recipe and the structural mismatch with this client's usual stream envelope.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._fast_asset_ctxs_impl())

  async def _fast_asset_ctxs_impl(self):
    stream = await self.subscribe('fastAssetCtxs')

    def mapper(msg) -> str:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
