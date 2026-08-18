"""`/contractAccount/wallet` — Subscribe to the authenticated account's futures wallet balance pushes -- fires whenever a trade, transfer, margin change, or funding settlement changes the futures account's balance, per settlement currency."""

from typing_extensions import Any, NotRequired
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.types import WsSubscriptionAck
from kucoin.core import StreamEndpoint


class FuturesBalanceEvent(TypedDict):
  """One futures wallet balance snapshot, for one settlement currency -- the unwrapped `data` field of the raw WebSocket frame (`SocketStreamClient.authed_subscribe` extracts `data` before handing the stream to the caller; see `spec/core.md`'s WebSocket section)."""

  currency: str
  """Settlement currency this balance is denominated in, for example `USDT` or `XBT`."""
  walletBalance: str
  """Total wallet balance."""
  availableBalance: str
  """Balance available for trading or withdrawal."""
  holdBalance: str
  """Frozen balance."""
  equity: str
  """Total account equity."""
  crossPosMargin: str
  """Margin used by cross-margin positions."""
  crossOrderMargin: str
  """Margin used by open cross-margin orders."""
  totalCrossMargin: str
  """Total cross margin in use (positions plus orders)."""
  crossUnPnl: str
  """Unrealized PnL across cross-margin positions."""
  isolatedPosMargin: str
  """Margin used by isolated-margin positions."""
  isolatedOrderMargin: str
  """Margin used by open isolated-margin orders."""
  isolatedFundingFeeMargin: str
  """Isolated-margin funding-fee reserve."""
  isolatedUnPnl: str
  """Unrealized PnL across isolated-margin positions."""
  maxWithdrawAmount: NotRequired[str]
  """Maximum amount currently withdrawable. Present on the live docs-new page and its worked example, but absent from KuCoin's machine-readable WS spec's field list for this channel -- kept as documented, not required, since this pass never observed a real push to confirm it (see `unverified`)."""
  version: str
  """Balance version number, incremented on every change -- can be used to detect out-of-order pushes."""
  timestamp: str
  """Millisecond epoch of this push, sent as a numeric string -- unlike most KuCoin REST timestamp fields, which are real JSON integers."""


_Type = FuturesBalanceEvent
validate_update = validator[_Type](_Type)  # type: ignore


class Balance(StreamEndpoint):
  """Subscribe to `/contractAccount/wallet` — mixed into `Private`, the product exposing `streams.futures.balance`."""

  def balance(
    self,
    *,
    validate: bool | None = None,
  ) -> StreamManager[FuturesBalanceEvent, Any, Any]:
    """Subscribe to the authenticated account's futures wallet balance pushes -- fires whenever a trade, transfer, margin change, or funding settlement changes the futures account's balance, per settlement currency.

    Args:
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    Raises:
      AuthError: This connection has no credentials — this is a private channel, unreachable from a `public=True` client.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.authed_subscribe(
      '/contractAccount/wallet',
      validator=validate_update,
      validate=validate,
    )
