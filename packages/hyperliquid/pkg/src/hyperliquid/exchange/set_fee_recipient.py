from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class PerpDeployDefaultResponse(TypedDict):
  """Acknowledgement returned for a perpDeploy action that carries no per-item batch data."""

  type: Literal['default']
  """Fixed response-kind discriminator for this action."""


class SetFeeRecipientSubAction(TypedDict):
  dex: str
  feeRecipient: str


class SetFeeRecipientAction(TypedDict):
  type: Literal['perpDeploy']
  setFeeRecipient: SetFeeRecipientSubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[PerpDeployDefaultResponse])


class SetFeeRecipient(ExchangeMixin):
  async def set_fee_recipient(
    self,
    *,
    dex: str,
    fee_recipient: str,
    expires_after: int | None = None,
  ) -> ExchangeResponse[PerpDeployDefaultResponse]:
    """Designate the address that receives deployer fees for a HIP-3 perp dex through Hyperliquid POST /exchange using perpDeploy sub-action `setFeeRecipient`.

    Args:
      dex: Name of the perp dex.
      fee_recipient: Address that should receive this dex's deployer fees.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions)
    """
    ts = timestamp.now()
    sub_action: SetFeeRecipientSubAction = {
      'dex': dex,
      'feeRecipient': fee_recipient,
    }
    action: SetFeeRecipientAction = {
      'type': 'perpDeploy',
      'setFeeRecipient': sub_action,
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
