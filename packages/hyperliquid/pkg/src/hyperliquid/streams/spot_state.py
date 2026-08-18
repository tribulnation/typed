from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class SpotBalance(TypedDict):
  """A single spot token balance."""

  coin: str
  """Spot asset symbol, e.g. "USDC" or "HYPE"."""
  token: int
  """Spot token index."""
  hold: str
  """Amount of the balance currently held (locked) by open orders."""
  total: str
  """Total balance of the token, including any amount on hold."""
  entryNtl: str
  """Notional value of the balance at acquisition."""


class SpotStateSubscriptionEcho(TypedDict):
  """Echo of the spotState subscription that was acknowledged."""

  type: Literal['spotState']
  """Subscription channel identifier."""
  user: str
  """Wallet address the subscription is scoped to."""
  ignorePortfolioMargin: bool
  """Whether portfolio-margin balances are excluded from this subscription, echoed back; defaults to `false` when omitted from the request. Named `isPortfolioMargin` in upstream docs -- see `notes`."""


class SpotStateSubscriptionParams(TypedDict):
  """Spot state subscription parameters: user address, plus an optional portfolio-margin exclusion flag."""

  user: str
  """Wallet address to subscribe to spot state updates for."""
  ignorePortfolioMargin: NotRequired[bool]
  """Optional: exclude portfolio-margin balances from this subscription. Defaults to `false` when omitted. Named `isPortfolioMargin` in upstream docs -- see `notes`."""


class SpotState(TypedDict):
  """The subscribed user's spot balances snapshot."""

  balances: list[SpotBalance]
  """The user's spot token balances."""


class SpotStateSubscribeAck(TypedDict):
  """Acknowledgement of a spotState subscribe/unsubscribe request."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: SpotStateSubscriptionEcho


class WsSpotStateUpdate(TypedDict):
  """Pushed spot state snapshot for the subscribed user."""

  user: str
  """Wallet address this update is scoped to."""
  spotState: SpotState


adapter = pydantic.TypeAdapter(WsSpotStateUpdate)


class SpotStateEndpoint(StreamsMixin):
  def spot_state(self, user: str, *, ignore_portfolio_margin: bool | None = None):
    """Subscribe to Hyperliquid `spotState` updates: a user's spot token balances.

    Args:
      user: Wallet address to subscribe to spot state updates for.
      ignore_portfolio_margin: Optional: exclude portfolio-margin balances from this subscription. Defaults to `false` when omitted. Named `isPortfolioMargin` in upstream docs -- see `notes`.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(
      lambda: self._spot_state_impl(
        user, ignore_portfolio_margin=ignore_portfolio_margin
      )
    )

  async def _spot_state_impl(
    self,
    user: str,
    *,
    ignore_portfolio_margin: bool | None = None,
  ):
    params: dict[str, object] = {
      'user': user,
    }
    if ignore_portfolio_margin is not None:
      params['ignorePortfolioMargin'] = ignore_portfolio_margin
    stream = await self.subscribe('spotState', params)

    def mapper(msg) -> WsSpotStateUpdate:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
