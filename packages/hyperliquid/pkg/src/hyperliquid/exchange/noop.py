from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class NoopAction(TypedDict):
  type: Literal['noop']


class NoopActionResult(TypedDict):
  """Result of an accepted no-op action."""

  type: Literal['default']
  """Discriminator confirming this is a no-op result. The venue carries no further data alongside it."""


adapter = pydantic.TypeAdapter(ExchangeResponse[NoopActionResult])


class Noop(ExchangeMixin):
  async def noop(
    self,
    *,
    expires_after: int | None = None,
  ) -> ExchangeResponse[NoopActionResult]:
    """Mark a nonce as used without otherwise doing anything, through Hyperliquid POST /exchange using action type `noop`. A more reliable way to invalidate an in-flight order's nonce than sending a `cancel`.

    Args:
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: NoopAction = {
      'type': 'noop',
    }
    sig = sign_l1_action(
      action,
      wallet=self.wallet,
      nonce=ts,
      mainnet=self.mainnet,
      vault_address=None,
      expires_after=expires_after,
    )
    result = await self.client.request(
      {
        'action': action,
        'nonce': ts,
        'signature': sig,
        'vaultAddress': None,
        'expiresAfter': expires_after,
      }
    )
    return adapter.validate_python(result) if self.validate else result
