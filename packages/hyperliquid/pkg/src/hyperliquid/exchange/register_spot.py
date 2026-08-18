from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class Data(TypedDict):
  """Empty object accompanying `type` on every other captured non-batch exchange action on this venue; whether spotDeploy sub-actions echo it too is unconfirmed."""


class RegisterSpotAction(TypedDict):
  type: Literal['spotDeploy']
  registerSpot: tuple[int, int]


class DefaultResponse(TypedDict):
  """Default per-action response payload, echoed on success."""

  type: str
  """Response discriminator. Every captured non-batch exchange action on this venue returns either the literal 'default' or its own action-type string here; which applies to a spotDeploy sub-action is unconfirmed (see this endpoint's notes)."""
  data: NotRequired[Data]


adapter = pydantic.TypeAdapter(ExchangeResponse[DefaultResponse])


class RegisterSpot(ExchangeMixin):
  async def register_spot(
    self,
    *,
    tokens: tuple[int, int],
    expires_after: int | None = None,
  ) -> ExchangeResponse[DefaultResponse]:
    """Deploy a spot trading pair between a base and quote token through Hyperliquid POST /exchange using action type `spotDeploy` with sub-action `registerSpot`. Fourth of the five-step HIP-1/HIP-2 token deployment sequence; also the action used to pair two already-existing tokens, which instead runs an independent Dutch auction whose status is available from info.spot_pair_deploy_auction_status.

    Args:
      tokens: The (base token index, quote token index) pair to register as a spot market.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets)
    """
    ts = timestamp.now()
    action: RegisterSpotAction = {'type': 'spotDeploy', 'registerSpot': tokens}
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
