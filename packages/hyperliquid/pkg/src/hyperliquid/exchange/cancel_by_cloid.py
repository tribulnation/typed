from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class CancelByCloidRequestItemCancelByCloidCancelsItem(TypedDict):
  """One order to cancel, identified by its client order id."""

  asset: int
  """Asset index the order to cancel trades, per `info.meta`'s `universe` ordering."""
  cloid: str
  """Client order id of the order to cancel: a 128-bit hex string, e.g. `0x1234567890abcdef1234567890abcdef`."""


class CancelByCloidRequestItemParameterCancelsItem(TypedDict):
  """One order to cancel, identified by its client order id."""

  asset: int
  """Asset index the order to cancel trades, per `info.meta`'s `universe` ordering."""
  cloid: str
  """Client order id of the order to cancel: a 128-bit hex string, e.g. `0x1234567890abcdef1234567890abcdef`."""


class CancelStatusError(TypedDict):
  """Outcome for a cancel the venue rejected individually within an otherwise-accepted batch."""

  error: str
  """Reason this specific cancel was rejected, e.g. 'Order was never placed, already canceled, or filled.'."""


class CancelByCloidAction(TypedDict):
  type: Literal['cancelByCloid']
  cancels: list[CancelByCloidRequestItemCancelByCloidCancelsItem]
  f: NotRequired[bool]


class CancelByCloidActionData(TypedDict):
  """Per-cancel outcomes for this action."""

  statuses: list[CancelStatusError | Literal['success']]
  """One entry per cancel in the request, in the same order."""


class CancelByCloidActionResult(TypedDict):
  """Result of an accepted cancel-by-cloid action."""

  type: Literal['cancel']
  """Discriminator confirming this is a cancel result. The venue answers `cancelByCloid` with the same `cancel` type the plain cancel action uses, not a distinct `cancelByCloid` type."""
  data: CancelByCloidActionData


adapter = pydantic.TypeAdapter(ExchangeResponse[CancelByCloidActionResult])


class CancelByCloid(ExchangeMixin):
  async def cancel_by_cloid(
    self,
    *,
    cancels: list[CancelByCloidRequestItemParameterCancelsItem],
    f: bool | None = None,
    vault_address: str | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[CancelByCloidActionResult]:
    """Cancel one or more resting orders by their caller-chosen client order id, through Hyperliquid POST /exchange using action type `cancelByCloid`.

    Args:
      cancels: Cancels to submit, one entry per order to cancel.
      f: Fast-cancel path. Rejected if any cancel in this batch refers to a trigger order. Omitted when false.
      vault_address: Optional vault address for the signed action.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: CancelByCloidAction = {
      'type': 'cancelByCloid',
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
