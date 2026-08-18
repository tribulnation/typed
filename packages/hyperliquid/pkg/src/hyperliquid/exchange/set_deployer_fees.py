from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class PerpDeployDefaultResponse(TypedDict):
  """Acknowledgement returned for a perpDeploy action that carries no per-item batch data."""

  type: Literal['default']
  """Fixed response-kind discriminator for this action."""


class PerpDeployFeeScaleDeployerFeesItemPrefix1(TypedDict):
  """Deployer fee scale settings for one asset."""

  scale: str
  """Fee scale, as a decimal string in `[0.0, 3.0]`, or `[0.0, 10.0)` when `growth_mode` is `true`. Scales the portion of the user fee routed to the protocol versus the deployer; see upstream docs for the exact split formula."""
  growth_mode: bool
  """Whether growth-mode fee scaling applies for this asset."""


class PerpDeployFeeScaleSetDeployerFeesItemPrefix1(TypedDict):
  """Deployer fee scale settings for one asset."""

  scale: str
  """Fee scale, as a decimal string in `[0.0, 3.0]`, or `[0.0, 10.0)` when `growth_mode` is `true`. Scales the portion of the user fee routed to the protocol versus the deployer; see upstream docs for the exact split formula."""
  growth_mode: bool
  """Whether growth-mode fee scaling applies for this asset."""


class SetDeployerFeesAction(TypedDict):
  type: Literal['perpDeploy']
  setDeployerFees: list[tuple[str, PerpDeployFeeScaleSetDeployerFeesItemPrefix1]]


adapter = pydantic.TypeAdapter(ExchangeResponse[PerpDeployDefaultResponse])


class SetDeployerFees(ExchangeMixin):
  async def set_deployer_fees(
    self,
    *,
    deployer_fees: list[tuple[str, PerpDeployFeeScaleDeployerFeesItemPrefix1]],
    expires_after: int | None = None,
  ) -> ExchangeResponse[PerpDeployDefaultResponse]:
    """Set per-asset deployer fee scaling on a HIP-3 perp dex through Hyperliquid POST /exchange using perpDeploy sub-action `setDeployerFees`. On mainnet, rate limited to one change per 30 days.

    Args:
      deployer_fees: A list, sorted by asset, of (asset, fee scale settings) pairs.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions)
    """
    ts = timestamp.now()
    action: SetDeployerFeesAction = {
      'type': 'perpDeploy',
      'setDeployerFees': deployer_fees,
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
