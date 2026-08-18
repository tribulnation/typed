from typing_extensions import Any, Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class OpenOrdersSubscriptionEcho(TypedDict):
  """Echo of the openOrders subscription that was acknowledged."""

  dex: str
  """Perp dex the subscription is scoped to; the empty string names the default (first) perp dex."""
  type: Literal['openOrders']
  """Subscription channel identifier."""
  user: str
  """Wallet address the subscription is scoped to."""


class OpenOrdersSubscriptionParams(TypedDict):
  """Open orders subscription parameters: user address and perp dex."""

  dex: str
  """Perp dex to subscribe on; the empty string names the default (first) perp dex."""
  user: str
  """Wallet address to subscribe to open orders for."""


class OpenOrdersUpdate(TypedDict):
  """Pushed snapshot of the subscribed user's open orders."""

  dex: str
  """Perp dex this update is scoped to; the empty string names the default (first) perp dex."""
  orders: list[dict[str, Any]]
  """This user's currently open orders on this dex; empty in every captured example, so the per-order record shape mirrors `info.open_orders`'s order records and is not independently modeled here."""
  user: str
  """Wallet address this update is scoped to."""


class OpenOrdersSubscribeAck(TypedDict):
  """Acknowledgement of an openOrders subscribe/unsubscribe request."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: OpenOrdersSubscriptionEcho


adapter = pydantic.TypeAdapter(OpenOrdersUpdate)


class OpenOrders(StreamsMixin):
  def open_orders(self, dex: str, user: str):
    """Subscribe to Hyperliquid `openOrders` updates.

    Args:
      dex: Perp dex to subscribe on; the empty string names the default (first) perp dex.
      user: Wallet address to subscribe to open orders for.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._open_orders_impl(dex, user))

  async def _open_orders_impl(self, dex: str, user: str):
    params: dict[str, object] = {
      'dex': dex,
      'user': user,
    }
    stream = await self.subscribe('openOrders', params)

    def mapper(msg) -> OpenOrdersUpdate:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
