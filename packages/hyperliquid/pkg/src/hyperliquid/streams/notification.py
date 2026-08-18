from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class Notification(TypedDict):
  """Pushed notification for the subscribed user."""

  notification: str
  """User-facing notification text, e.g. an order-fill or liquidation alert."""


class NotificationSubscriptionEcho(TypedDict):
  """Echo of the notification subscription that was acknowledged."""

  type: Literal['notification']
  """Subscription channel identifier."""
  user: str
  """Wallet address the subscription is scoped to."""


class NotificationSubscriptionParams(TypedDict):
  """Notification subscription parameters: the user address."""

  user: str
  """Wallet address to subscribe to notifications for."""


class NotificationSubscribeAck(TypedDict):
  """Acknowledgement of a notification subscribe/unsubscribe request."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: NotificationSubscriptionEcho


adapter = pydantic.TypeAdapter(Notification)


class NotificationEndpoint(StreamsMixin):
  def notification(self, user: str):
    """Subscribe to Hyperliquid `notification` updates.

    Args:
      user: Wallet address to subscribe to notifications for.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._notification_impl(user))

  async def _notification_impl(self, user: str):
    params: dict[str, object] = {
      'user': user,
    }
    stream = await self.subscribe('notification', params)

    def mapper(msg) -> Notification:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
