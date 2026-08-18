from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class PerpDeployDefaultResponse(TypedDict):
  """Acknowledgement returned for a perpDeploy action that carries no per-item batch data."""

  type: Literal['default']
  """Fixed response-kind discriminator for this action."""


class PerpDeploySubDeployerInputParameterSubDeployersItem(TypedDict):
  """One modification to sub-deployer permissions."""

  variant: Literal[
    'registerAsset2',
    'registerAsset',
    'setOracle',
    'setFundingMultipliers',
    'setFundingInterestRates',
    'haltTrading',
    'setMarginTableIds',
    'setFeeRecipient',
    'setOpenInterestCaps',
    'setSubDeployers',
    'setMarginModes',
    'setDeployerFees',
    'setPerpAnnotation',
    'disableDex',
  ]
  """Which perpDeploy action this permission grant applies to (the sub-action key the sub-deployer is being authorized, or unauthorized, to call)."""
  user: str
  """Address of the sub-deployer."""
  allowed: bool
  """Whether to add (`true`) or remove (`false`) this user from the authorized set for `variant`."""


class PerpDeploySubDeployerInputSubSubDeployersItem(TypedDict):
  """One modification to sub-deployer permissions."""

  variant: Literal[
    'registerAsset2',
    'registerAsset',
    'setOracle',
    'setFundingMultipliers',
    'setFundingInterestRates',
    'haltTrading',
    'setMarginTableIds',
    'setFeeRecipient',
    'setOpenInterestCaps',
    'setSubDeployers',
    'setMarginModes',
    'setDeployerFees',
    'setPerpAnnotation',
    'disableDex',
  ]
  """Which perpDeploy action this permission grant applies to (the sub-action key the sub-deployer is being authorized, or unauthorized, to call)."""
  user: str
  """Address of the sub-deployer."""
  allowed: bool
  """Whether to add (`true`) or remove (`false`) this user from the authorized set for `variant`."""


class SetSubDeployersSubAction(TypedDict):
  dex: str
  subDeployers: list[PerpDeploySubDeployerInputSubSubDeployersItem]


class SetSubDeployersAction(TypedDict):
  type: Literal['perpDeploy']
  setSubDeployers: SetSubDeployersSubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[PerpDeployDefaultResponse])


class SetSubDeployers(ExchangeMixin):
  async def set_sub_deployers(
    self,
    *,
    dex: str,
    sub_deployers: list[PerpDeploySubDeployerInputParameterSubDeployersItem],
    expires_after: int | None = None,
  ) -> ExchangeResponse[PerpDeployDefaultResponse]:
    """Add or remove sub-deployer permissions, scoped to individual perpDeploy action variants, for a HIP-3 perp dex through Hyperliquid POST /exchange using perpDeploy sub-action `setSubDeployers`.

    Args:
      dex: Name of the perp dex.
      sub_deployers: The sub-deployer permission changes to apply, in order.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions)
    """
    ts = timestamp.now()
    sub_action: SetSubDeployersSubAction = {
      'dex': dex,
      'subDeployers': sub_deployers,
    }
    action: SetSubDeployersAction = {
      'type': 'perpDeploy',
      'setSubDeployers': sub_action,
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
