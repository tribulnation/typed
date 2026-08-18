from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class ScheduleCancelAction(TypedDict):
  type: Literal['scheduleCancel']
  time: NotRequired[int]


class ScheduleCancelActionResult(TypedDict):
  """Result of an accepted schedule-cancel action."""

  type: str
  """Discriminator for a schedule-cancel result. Not directly observed live -- every captured example was rejected -- so left as a bare string rather than a guessed literal."""


adapter = pydantic.TypeAdapter(ExchangeResponse[ScheduleCancelActionResult])


class ScheduleCancel(ExchangeMixin):
  async def schedule_cancel(
    self,
    *,
    time: int | None = None,
    vault_address: str | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[ScheduleCancelActionResult]:
    """Schedule a cancel-all operation at a future time, through Hyperliquid POST /exchange using action type `scheduleCancel`. Once the time comes, all open orders are canceled and a daily trigger count (max 10, reset at 00:00 UTC) is incremented.

    Args:
      time: Unix epoch milliseconds at which to cancel all open orders; must be at least 5 seconds in the future. Omit to clear a previously scheduled cancel.
      vault_address: Optional vault address for the signed action.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: ScheduleCancelAction = {
      'type': 'scheduleCancel',
    }
    if time is not None:
      action['time'] = time
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
