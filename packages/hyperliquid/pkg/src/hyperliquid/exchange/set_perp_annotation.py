from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class PerpDeployDefaultResponse(TypedDict):
  """Acknowledgement returned for a perpDeploy action that carries no per-item batch data."""

  type: Literal['default']
  """Fixed response-kind discriminator for this action."""


class SetPerpAnnotationSubAction(TypedDict):
  coin: str
  category: str
  description: str
  displayName: str | None
  keywords: list[str]


class SetPerpAnnotationAction(TypedDict):
  type: Literal['perpDeploy']
  setPerpAnnotation: SetPerpAnnotationSubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[PerpDeployDefaultResponse])


class SetPerpAnnotation(ExchangeMixin):
  async def set_perp_annotation(
    self,
    *,
    coin: str,
    category: str,
    description: str,
    display_name: str | None,
    keywords: list[str],
    expires_after: int | None = None,
  ) -> ExchangeResponse[PerpDeployDefaultResponse]:
    """Set display metadata (category, description, display name, keywords) for one asset on a HIP-3 perp dex through Hyperliquid POST /exchange using perpDeploy sub-action `setPerpAnnotation`.

    Args:
      coin: Ticker of the asset being annotated.
      category: Display category for the asset, at most 15 characters. The venue does not publish a closed set of category values, so this is left as a free-form string.
      description: Display description for the asset, at most 400 characters.
      display_name: Display name for the asset, at most 9 characters, or `null` to clear it.
      keywords: Search keywords for the asset, at most 2 entries.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions)
    """
    ts = timestamp.now()
    sub_action: SetPerpAnnotationSubAction = {
      'coin': coin,
      'category': category,
      'description': description,
      'displayName': display_name,
      'keywords': keywords,
    }
    action: SetPerpAnnotationAction = {
      'type': 'perpDeploy',
      'setPerpAnnotation': sub_action,
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
