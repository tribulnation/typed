from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class PerpDeployDefaultResponse(TypedDict):
  """Acknowledgement returned for a perpDeploy action that carries no per-item batch data."""

  type: Literal['default']
  """Fixed response-kind discriminator for this action."""


class SetMarginTableIdsAction(TypedDict):
  type: Literal['perpDeploy']
  setMarginTableIds: list[tuple[str, int]]


adapter = pydantic.TypeAdapter(ExchangeResponse[PerpDeployDefaultResponse])


class SetMarginTableIds(ExchangeMixin):
  async def set_margin_table_ids(
    self,
    *,
    margin_table_ids: list[tuple[str, int]],
    expires_after: int | None = None,
  ) -> ExchangeResponse[PerpDeployDefaultResponse]:
    """Map assets on a HIP-3 perp dex to margin table ids through Hyperliquid POST /exchange using perpDeploy sub-action `setMarginTableIds`.

    Args:
      margin_table_ids: A list, sorted by asset, of (asset, margin table id) pairs.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions)
    """
    ts = timestamp.now()
    action: SetMarginTableIdsAction = {
      'type': 'perpDeploy',
      'setMarginTableIds': margin_table_ids,
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
