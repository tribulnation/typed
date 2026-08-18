"""`/margin/isolatedPosition:{symbol}` — Subscribe to the authenticated account's isolated-margin position pushes for one isolated symbol -- fires when the position's status changes (borrow, repay, liquidation, auto-renew) or, periodically, while the position carries a liability."""

from typing_extensions import Any, Literal
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class IsolatedMarginAssetChange(TypedDict):
  """One currency leg of an isolated-margin position change."""

  total: str
  """Total balance of this currency in the position."""
  hold: str
  """Amount of this currency on hold."""
  liabilityPrincipal: str
  """Outstanding borrow principal in this currency."""
  liabilityInterest: str
  """Accrued, unpaid interest in this currency."""


class IsolatedMarginPositionEvent(TypedDict):
  """One isolated-margin position change -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.authed_subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section). The wire frame's `subject` field is always `positionChange` on this channel -- unlike Cross Margin Position, there is no second push shape to disambiguate, so it carries no information the caller needs and is stripped along with the rest of the envelope."""

  tag: str
  """Isolated margin symbol this position belongs to, for example `BTC-USDT`."""
  status: Literal[
    'DEBT', 'CLEAR', 'IN_BORROW', 'IN_REPAY', 'IN_LIQUIDATION', 'IN_AUTO_RENEW'
  ]
  """Position status."""
  statusBizType: Literal[
    'FORCE_LIQUIDATION',
    'USER_BORROW',
    'TRADE_AUTO_BORROW',
    'USER_REPAY',
    'AUTO_REPAY',
    'DEFAULT_DEBT',
    'DEFAULT_CLEAR',
    'ONE_CLICK_LIQUIDATION',
    'B2C_INTEREST_SETTLE_LIQUIDATION',
    'AIR_DROP_LIQUIDATION',
  ]
  """What triggered this status change."""
  accumulatedPrincipal: str
  """Accumulated borrow principal for this position."""
  changeAssets: dict[str, IsolatedMarginAssetChange]
  """Per-currency asset/liability amounts, keyed by currency code (for example `BTC`, `USDT`)."""
  timestamp: int
  """Unix milliseconds when this push was generated."""


_Type = IsolatedMarginPositionEvent
validate_update = validator[_Type](_Type)  # type: ignore


class IsolatedMarginPosition(StreamEndpoint):
  """Subscribe to `/margin/isolatedPosition:{symbol}` — mixed into `Private`, the product exposing `streams.spot_margin.isolated_margin_position`."""

  def isolated_margin_position(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[IsolatedMarginPositionEvent, Any, Any]:
    """Subscribe to the authenticated account's isolated-margin position pushes for one isolated symbol -- fires when the position's status changes (borrow, repay, liquidation, auto-renew) or, periodically, while the position carries a liability.

    Args:
      symbol: Isolated margin symbol to watch, for example `BTC-USDT`.
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    Raises:
      AuthError: This connection has no credentials — this is a private channel, unreachable from a `public=True` client.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.authed_subscribe(
      f'/margin/isolatedPosition:{symbol}',
      validator=validate_update,
      validate=validate,
    )
