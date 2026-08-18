from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class UserFundingsSubscription(TypedDict):
  """Subscription parameters that were acknowledged."""

  type: Literal['userFundings']
  """Subscription channel identifier."""
  user: str
  """The account address whose activity this subscription tracks."""


class UserFundingsSubscriptionParams(TypedDict):
  """Identifies the account whose funding payments to subscribe to."""

  user: str
  """The account address whose activity this subscription tracks."""


class WsUserFunding(TypedDict):
  """One historical or streamed funding payment for the user."""

  time: int
  """Millisecond epoch timestamp when the funding payment was applied."""
  coin: str
  """Perp coin symbol the funding payment applies to."""
  usdc: str
  """Funding payment amount in USDC (negative when paid by the user, positive when received)."""
  szi: str
  """Signed position size the funding was computed against."""
  fundingRate: str
  """Hourly funding rate applied for this payment."""


class UserFundingsSubscribeAck(TypedDict):
  """Echo of the subscription that was acknowledged."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: UserFundingsSubscription


class UserFundingsUpdate(TypedDict):
  """Snapshot or incremental update of the user's funding payment history."""

  isSnapshot: bool
  """True on the initial snapshot message; false on each subsequent streamed update."""
  user: str
  """The account address whose activity this subscription tracks."""
  fundings: list[WsUserFunding]
  """Funding payments in this snapshot or update, oldest first."""


adapter = pydantic.TypeAdapter(UserFundingsUpdate)


class UserFundings(StreamsMixin):
  def user_fundings(self, user: str):
    """Subscribe to a user's funding payments: an initial snapshot of recent payments followed by streamed payments on the hour.

    Args:
      user: The account address whose activity this subscription tracks.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._user_fundings_impl(user))

  async def _user_fundings_impl(self, user: str):
    params: dict[str, object] = {
      'user': user,
    }
    stream = await self.subscribe('userFundings', params)

    def mapper(msg) -> UserFundingsUpdate:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
