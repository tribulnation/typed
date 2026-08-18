from typing_extensions import Any, Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.streams.core import StreamsMixin
from typed_core.util import StreamManager


class ClearinghouseStateSubscriptionEcho(TypedDict):
  """Echo of the clearinghouseState subscription that was acknowledged."""

  dex: str
  """Perp dex the subscription is scoped to; the empty string names the default (first) perp dex."""
  type: Literal['clearinghouseState']
  """Subscription channel identifier."""
  user: str
  """Wallet address the subscription is scoped to."""


class ClearinghouseStateSubscriptionParams(TypedDict):
  """Clearinghouse state subscription parameters: user address and perp dex."""

  dex: str
  """Perp dex to subscribe on; the empty string names the default (first) perp dex."""
  user: str
  """Wallet address to subscribe to clearinghouse state updates for."""


class MarginSummaryCrossMarginSummary(TypedDict):
  """Cross-margin account summary: value, margin used, and notional position size."""

  accountValue: str
  """Total account value (equity), in USD."""
  totalMarginUsed: str
  """Total margin currently used."""
  totalNtlPos: str
  """Total notional value of open positions."""
  totalRawUsd: str
  """Total raw USD balance, before unrealized PnL."""


class MarginSummaryMarginSummary(TypedDict):
  """Overall (cross + isolated) account summary: value, margin used, and notional position size."""

  accountValue: str
  """Total account value (equity), in USD."""
  totalMarginUsed: str
  """Total margin currently used."""
  totalNtlPos: str
  """Total notional value of open positions."""
  totalRawUsd: str
  """Total raw USD balance, before unrealized PnL."""


class ClearinghouseState(TypedDict):
  """Full margin/positions snapshot for the subscribed user on the subscribed dex."""

  assetPositions: list[dict[str, Any]]
  """Open perp positions for this user on this dex; empty in every captured example, so the per-position record shape mirrors `info.clearinghouse_state`'s `assetPositions` and is not independently modeled here."""
  crossMaintenanceMarginUsed: str
  """Maintenance margin currently used by cross-margined positions."""
  crossMarginSummary: MarginSummaryCrossMarginSummary
  marginSummary: MarginSummaryMarginSummary
  time: int
  """Millisecond epoch timestamp this state was computed at."""
  withdrawable: str
  """Amount currently withdrawable, in USD."""


class ClearinghouseStateSubscribeAck(TypedDict):
  """Acknowledgement of a clearinghouseState subscribe/unsubscribe request."""

  method: Literal['subscribe', 'unsubscribe']
  """Which operation this acknowledgement answers."""
  subscription: ClearinghouseStateSubscriptionEcho


class ClearinghouseStateUpdate(TypedDict):
  """Pushed clearinghouse state snapshot for the subscribed user."""

  clearinghouseState: ClearinghouseState
  dex: str
  """Perp dex this update is scoped to; the empty string names the default (first) perp dex."""
  user: str
  """Wallet address this update is scoped to."""


adapter = pydantic.TypeAdapter(ClearinghouseStateUpdate)


class ClearinghouseStateEndpoint(StreamsMixin):
  def clearinghouse_state(self, dex: str, user: str):
    """Subscribe to Hyperliquid `clearinghouseState` updates.

    Args:
      dex: Perp dex to subscribe on; the empty string names the default (first) perp dex.
      user: Wallet address to subscribe to clearinghouse state updates for.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions)
    """
    return StreamManager(lambda: self._clearinghouse_state_impl(dex, user))

  async def _clearinghouse_state_impl(self, dex: str, user: str):
    params: dict[str, object] = {
      'dex': dex,
      'user': user,
    }
    stream = await self.subscribe('clearinghouseState', params)

    def mapper(msg) -> ClearinghouseStateUpdate:
      return adapter.validate_python(msg) if self.validate else msg

    return stream.map(mapper)
