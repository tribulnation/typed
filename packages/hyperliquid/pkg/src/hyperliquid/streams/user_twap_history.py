from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class TwapHistoryStatus(TypedDict):
  """TWAP order lifecycle status at the time of this history entry."""

  status: Literal['activated', 'terminated', 'finished', 'error']
  """Lifecycle status of the TWAP order."""
  description: str
  """Human-readable detail about the status, e.g. an error message."""


class TwapState(TypedDict):
  """Current state of one TWAP order."""

  coin: str
  """Perp or spot coin symbol the TWAP order trades."""
  user: str
  """Account address that placed the TWAP order."""
  side: Literal['B', 'A']
  """Order side: `B` (bid/buy) or `A` (ask/sell)."""
  sz: str
  """Total order size."""
  executedSz: str
  """Size executed so far."""
  executedNtl: str
  """Notional value executed so far."""
  minutes: int
  """Duration of the TWAP execution window, in minutes."""
  reduceOnly: bool
  """Whether the order is restricted to reducing an existing position."""
  randomize: bool
  """Whether slice timing is randomized within each interval."""
  timestamp: int
  """Millisecond epoch timestamp when the TWAP order was placed."""


class UserTwapHistorySubscription(TypedDict):
  """Subscription parameters that were acknowledged."""

  type: Literal['userTwapHistory']
  """Subscription channel identifier."""
  user: str
  """The account address whose activity this subscription tracks."""


class UserTwapHistorySubscriptionParams(TypedDict):
  """Identifies the account whose TWAP order history to subscribe to."""

  user: str
  """The account address whose activity this subscription tracks."""


class UserTwapHistorySubscribeAck(TypedDict):
  """Echo of the subscription that was acknowledged."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: UserTwapHistorySubscription


class WsTwapHistory(TypedDict):
  """One historical status change of a TWAP order."""

  state: TwapState
  status: TwapHistoryStatus
  time: int
  """Millisecond epoch timestamp of this history entry."""


class UserTwapHistoryUpdate(TypedDict):
  """Snapshot or incremental update of the user's TWAP order history."""

  isSnapshot: bool
  """True on the initial snapshot message; false on each subsequent streamed update."""
  user: str
  """The account address whose activity this subscription tracks."""
  history: list[WsTwapHistory]
  """TWAP order history entries in this snapshot or update, oldest first."""


adapter = pydantic.TypeAdapter(UserTwapHistoryUpdate)


class UserTwapHistory(StreamsMixin):
  def user_twap_history(self, user: str):
    """Subscribe to a user's TWAP order history: an initial snapshot followed by streamed status changes.

    Args:
      user: The account address whose activity this subscription tracks.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._user_twap_history_impl(user))

  async def _user_twap_history_impl(self, user: str):
    params: dict[str, object] = {
      'user': user,
    }
    stream = await self.subscribe('userTwapHistory', params)

    def mapper(msg) -> UserTwapHistoryUpdate:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
