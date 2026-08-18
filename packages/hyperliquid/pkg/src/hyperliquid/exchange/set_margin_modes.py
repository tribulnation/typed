from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class PerpDeployDefaultResponse(TypedDict):
  """Acknowledgement returned for a perpDeploy action that carries no per-item batch data."""

  type: Literal['default']
  """Fixed response-kind discriminator for this action."""


class SetMarginModesAction(TypedDict):
  type: Literal['perpDeploy']
  setMarginModes: list[tuple[str, Literal['strictIsolated', 'noCross']]]


adapter = pydantic.TypeAdapter(ExchangeResponse[PerpDeployDefaultResponse])


class SetMarginModes(ExchangeMixin):
  async def set_margin_modes(
    self,
    *,
    margin_modes: list[tuple[str, Literal['strictIsolated', 'noCross']]],
    expires_after: int | None = None,
  ) -> ExchangeResponse[PerpDeployDefaultResponse]:
    """Set per-asset margin modes on a HIP-3 perp dex through Hyperliquid POST /exchange using perpDeploy sub-action `setMarginModes`.

    Args:
      margin_modes: A list, sorted by asset, of (asset, margin mode) pairs.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions)
    """
    ts = timestamp.now()
    action: SetMarginModesAction = {
      'type': 'perpDeploy',
      'setMarginModes': margin_modes,
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
