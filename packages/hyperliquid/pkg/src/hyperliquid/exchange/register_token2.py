from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class Data(TypedDict):
  """Empty object accompanying `type` on every other captured non-batch exchange action on this venue; whether spotDeploy sub-actions echo it too is unconfirmed."""


class SpotDeployTokenSpec(TypedDict):
  name: str
  """The token's short ticker name."""
  sz_decimals: int
  """Number of decimals used for order sizes of this token."""
  wei_decimals: int
  """Number of decimals used for the token's smallest on-chain unit (wei)."""


class DefaultResponse(TypedDict):
  """Default per-action response payload, echoed on success."""

  type: str
  """Response discriminator. Every captured non-batch exchange action on this venue returns either the literal 'default' or its own action-type string here; which applies to a spotDeploy sub-action is unconfirmed (see this endpoint's notes)."""
  data: NotRequired[Data]


class RegisterToken2subAction(TypedDict):
  spec: SpotDeployTokenSpec
  maxGas: float
  fullName: NotRequired[str]


class RegisterToken2action(TypedDict):
  type: Literal['spotDeploy']
  registerToken2: RegisterToken2subAction


adapter = pydantic.TypeAdapter(ExchangeResponse[DefaultResponse])


class RegisterToken2(ExchangeMixin):
  async def register_token2(
    self,
    *,
    spec: SpotDeployTokenSpec,
    max_gas: float,
    full_name: str | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[DefaultResponse]:
    """Register a new HIP-1 token through Hyperliquid POST /exchange using action type `spotDeploy` with sub-action `registerToken2`. First of the five-step HIP-1/HIP-2 token deployment sequence: initializes the token's specification and bids the maximum gas the deployer is willing to pay in the live token-registration Dutch auction (see info.spot_deploy_state's `gasAuction`).

    Args:
      spec: Token specification: name and decimal precision.
      max_gas: Maximum gas the deployer is willing to pay in the token-registration Dutch auction, denominated in the auction's own gas units (see info.spot_deploy_state's `gasAuction.currentGas`).
      full_name: Optional human-readable full name for the token, distinct from `spec.name`'s short ticker.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets)
    """
    ts = timestamp.now()
    sub_action: RegisterToken2subAction = {
      'spec': spec,
      'maxGas': max_gas,
    }
    if full_name is not None:
      sub_action['fullName'] = full_name
    action: RegisterToken2action = {'type': 'spotDeploy', 'registerToken2': sub_action}
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
