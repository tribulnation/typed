from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class TwapCancelAction(TypedDict):
  type: Literal['twapCancel']
  asset: int
  twapId: int


class TwapCancelStatusError(TypedDict):
  """Outcome for a TWAP cancel the venue rejected."""

  error: str
  """Reason the TWAP cancel was rejected, e.g. 'TWAP was never placed, already canceled, or filled.'."""


class TwapCancelActionData(TypedDict):
  """Outcome of this TWAP-cancel action."""

  status: Literal['success'] | TwapCancelStatusError
  """Outcome of the TWAP cancel: success, or rejected."""


class TwapCancelActionResult(TypedDict):
  """Result of an accepted TWAP-cancel action."""

  type: Literal['twapCancel']
  """Discriminator confirming this is a TWAP-cancel result."""
  data: TwapCancelActionData


adapter = pydantic.TypeAdapter(ExchangeResponse[TwapCancelActionResult])


class TwapCancel(ExchangeMixin):
  async def twap_cancel(
    self,
    *,
    asset: int,
    twap_id: int,
    vault_address: str | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[TwapCancelActionResult]:
    """Cancel a running TWAP order through Hyperliquid POST /exchange using action type `twapCancel`.

    Args:
      asset: Asset index the TWAP trades, per `info.meta`'s `universe` ordering.
      twap_id: Venue-assigned id of the TWAP to cancel, as returned by `twapOrder`.
      vault_address: Optional vault address for the signed action.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: TwapCancelAction = {
      'type': 'twapCancel',
      'asset': asset,
      'twapId': twap_id,
    }
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
