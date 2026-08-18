from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class CancelRequestItemCancelCancelsItem(TypedDict):
  """One order to cancel."""

  a: int
  """Asset index the order to cancel trades, per `info.meta`'s `universe` ordering."""
  o: int
  """Venue-assigned order id to cancel."""


class CancelRequestItemParameterCancelsItem(TypedDict):
  """One order to cancel."""

  a: int
  """Asset index the order to cancel trades, per `info.meta`'s `universe` ordering."""
  o: int
  """Venue-assigned order id to cancel."""


class CancelStatusError(TypedDict):
  """Outcome for a cancel the venue rejected individually within an otherwise-accepted batch."""

  error: str
  """Reason this specific cancel was rejected, e.g. 'Order was never placed, already canceled, or filled.'."""


class CancelAction(TypedDict):
  type: Literal['cancel']
  cancels: list[CancelRequestItemCancelCancelsItem]
  f: NotRequired[bool]


class CancelActionData(TypedDict):
  """Per-cancel outcomes for this action."""

  statuses: list[CancelStatusError | Literal['success']]
  """One entry per cancel in the request, in the same order."""


class CancelActionResult(TypedDict):
  """Result of an accepted cancel action."""

  type: Literal['cancel']
  """Discriminator confirming this is a cancel result."""
  data: CancelActionData


adapter = pydantic.TypeAdapter(ExchangeResponse[CancelActionResult])


class Cancel(ExchangeMixin):
  async def cancel(
    self,
    *,
    cancels: list[CancelRequestItemParameterCancelsItem],
    f: bool | None = None,
    vault_address: str | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[CancelActionResult]:
    """Cancel one or more resting orders through Hyperliquid POST /exchange using action type `cancel`.

    Args:
      cancels: Cancels to submit, one entry per order to cancel.
      f: Fast-cancel path. Rejected if any cancel in this batch refers to a trigger order. Omitted when false.
      vault_address: Optional vault address for the signed action.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: CancelAction = {
      'type': 'cancel',
      'cancels': cancels,
    }
    if f is not None:
      action['f'] = f
    sig = sign_l1_action(
      action,
      wallet=self.wallet,
      nonce=ts,
      mainnet=self.mainnet,
      vault_address=vault_address,
      expires_after=expires_after,
    )
    result = await self.client.request(
      {
        'action': action,
        'nonce': ts,
        'signature': sig,
        'vaultAddress': vault_address,
        'expiresAfter': expires_after,
      }
    )
    return adapter.validate_python(result) if self.validate else result
