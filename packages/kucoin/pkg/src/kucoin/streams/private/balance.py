"""`/account/balance` — Subscribe to account balance-change pushes."""

from typing_extensions import Any
from typed_core.util import StreamManager
from typed_core.validation import TypedDict, validator
from kucoin.core import StreamEndpoint


class BalanceRelation(TypedDict):
  """Order or trade the balance change is attributed to."""

  symbol: str
  orderId: str


class BalanceUpdate(TypedDict):
  """One account balance change, on the account/trade type the push arrived for."""

  accountId: str
  currency: str
  total: str
  """Total balance: `available + hold`."""
  available: str
  """Funds available to withdraw or trade."""
  hold: str
  """Funds on hold, not available for use."""
  availableChange: str
  holdChange: str
  relationContext: BalanceRelation
  relationEvent: str
  """What triggered the change, for example `trade.hold`."""
  relationEventId: str
  time: str
  """Millisecond epoch, sent as a numeric *string* on this channel — confirmed against
  the venue's own published schema, unlike every REST timestamp field (`kucoin.core.
  Timestamp`), which is a real JSON integer."""


validate_update = validator(BalanceUpdate)


class Balance(StreamEndpoint):
  """Subscribe to `/account/balance` — mixed into `Private`, the product exposing
  `streams.spot_margin.balance`."""

  def balance(
    self, *, validate: bool | None = None
  ) -> StreamManager[BalanceUpdate, Any, Any]:
    """Subscribe to the authenticated account's balance-change pushes — fires whenever a
    trade, transfer or hold changes a Spot/Margin/Trade account balance.

    Args:
      validate: Whether to validate pushed payloads against the expected schema.

    Returns:
      A manager for the subscription stream.

    Raises:
      AuthError: This connection has no credentials — this is a private channel,
        unreachable from a `public=True` client.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return self.authed_subscribe(
      '/account/balance', validator=validate_update, validate=validate
    )
