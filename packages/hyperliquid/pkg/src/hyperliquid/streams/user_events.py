from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class NonUserCancel(TypedDict):
  """One order canceled by the venue rather than the user."""

  coin: str
  """Asset symbol or spot asset id."""
  oid: int
  """Id of the order canceled by the venue rather than the user."""


class UserEventFillLiquidation(TypedDict):
  """Liquidation metadata, present only when this fill came from a liquidation."""

  liquidatedUser: NotRequired[str]
  """Address of the liquidated user."""
  markPx: float
  """Mark price at liquidation."""
  method: Literal['market', 'backstop']
  """Liquidation method."""


class UserEventFundingPayment(TypedDict):
  """One hourly funding payment."""

  time: int
  """Funding payment timestamp in epoch milliseconds."""
  coin: str
  """Coin the funding payment applies to."""
  usdc: str
  """Funding payment amount in USDC; negative means paid, positive means received."""
  szi: str
  """Signed position size at the time of the funding payment."""
  fundingRate: str
  """Funding rate applied."""


class UserEventLiquidationDetail(TypedDict):
  """Details of a liquidation involving the subscribed user."""

  lid: int
  """Liquidation id."""
  liquidator: str
  """Address of the liquidator."""
  liquidated_user: str
  """Address of the liquidated user."""
  liquidated_ntl_pos: str
  """Notional position size that was liquidated."""
  liquidated_account_value: str
  """Account value at the time of liquidation."""


class UserEventsSubscription(TypedDict):
  """Subscription parameters that were acknowledged."""

  type: Literal['userEvents']
  """Subscription channel identifier."""
  user: str
  """Address whose events are subscribed to."""


class UserEventsSubscriptionParams(TypedDict):
  """Subscription parameters for the `userEvents` channel."""

  user: str
  """Address whose events to subscribe to."""


class UserEventFill(TypedDict):
  """One fill belonging to the subscribed user."""

  coin: str
  """Asset symbol or spot asset id."""
  px: str
  """Fill price."""
  sz: str
  """Fill size."""
  side: Literal['A', 'B']
  """Side code: A (ask/sell) or B (bid/buy)."""
  time: int
  """Fill timestamp in epoch milliseconds."""
  startPosition: str
  """Position size before the fill."""
  dir: str
  """Human-readable fill direction, used for frontend display (e.g. "Open Long", "Close Short"); the venue documents no closed set of values."""
  closedPnl: str
  """Realized PnL closed by this fill."""
  hash: str
  """L1 transaction hash."""
  oid: int
  """Order id."""
  crossed: bool
  """Whether the order crossed the spread (was taker)."""
  fee: str
  """Fee paid; negative means a rebate was received."""
  tid: int
  """Unique trade id."""
  liquidation: NotRequired[UserEventFillLiquidation]
  feeToken: str
  """Token the fee was paid in."""
  builderFee: NotRequired[str]
  """Amount paid to the order's builder, already included in `fee`."""
  twapId: NotRequired[int | None]
  """TWAP order id when this fill came from a TWAP slice; null otherwise."""


class UserEventFunding(TypedDict):
  """User event carrying a single funding payment."""

  funding: UserEventFundingPayment


class UserEventLiquidation(TypedDict):
  """User event carrying a liquidation notice."""

  liquidation: UserEventLiquidationDetail


class UserEventNonUserCancel(TypedDict):
  """User event carrying venue-initiated order cancellations."""

  nonUserCancel: list[NonUserCancel]
  """Orders canceled by the venue rather than the user."""


class UserEventsSubscribeAck(TypedDict):
  """Echo of the subscription that was acknowledged."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: UserEventsSubscription


class UserEventFills(TypedDict):
  """User event carrying a batch of fills."""

  fills: list[UserEventFill]
  """Fills for the subscribed user."""


adapter = pydantic.TypeAdapter(
  UserEventFills | UserEventFunding | UserEventLiquidation | UserEventNonUserCancel
)


class UserEvents(StreamsMixin):
  def user_events(self, user: str):
    """Subscribe to Hyperliquid `userEvents` updates. Unlike every other channel, the venue pushes these on a raw `user` channel name rather than echoing `userEvents`.

    Args:
      user: Address whose events to subscribe to.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._user_events_impl(user))

  async def _user_events_impl(self, user: str):
    params: dict[str, object] = {
      'user': user,
    }
    stream = await self.subscribe('user', params, request_channel='userEvents')

    def mapper(
      msg,
    ) -> (
      UserEventFills | UserEventFunding | UserEventLiquidation | UserEventNonUserCancel
    ):
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
