from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class Data(TypedDict):
  """Empty object accompanying `type` on every other captured non-batch exchange action on this venue; whether spotDeploy sub-actions echo it too is unconfirmed."""


class GenesisSubAction(TypedDict):
  token: int
  maxSupply: str
  noHyperliquidity: NotRequired[bool]


class DefaultResponse(TypedDict):
  """Default per-action response payload, echoed on success."""

  type: str
  """Response discriminator. Every captured non-batch exchange action on this venue returns either the literal 'default' or its own action-type string here; which applies to a spotDeploy sub-action is unconfirmed (see this endpoint's notes)."""
  data: NotRequired[Data]


class GenesisAction(TypedDict):
  type: Literal['spotDeploy']
  genesis: GenesisSubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[DefaultResponse])


class Genesis(ExchangeMixin):
  async def genesis(
    self,
    *,
    token: int,
    max_supply: str,
    no_hyperliquidity: bool | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[DefaultResponse]:
    """Finalize the initial creation of a token with a maximum supply through Hyperliquid POST /exchange using action type `spotDeploy` with sub-action `genesis`. Third of the five-step HIP-1/HIP-2 token deployment sequence; `maxSupply` acts as a checksum that every prior `userGenesis` call succeeded as intended.

    Args:
      token: Index of the token being finalized, as registered by `registerToken2`.
      max_supply: Maximum token supply. Acts as a checksum that all prior `userGenesis` calls for this token succeeded as intended.
      no_hyperliquidity: When true, zeros the balance seeded for HIP-2 hyperliquidity (so `registerHyperliquidity`'s `nOrders` must then be 0).
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets)
    """
    ts = timestamp.now()
    sub_action: GenesisSubAction = {
      'token': token,
      'maxSupply': max_supply,
    }
    if no_hyperliquidity is not None:
      sub_action['noHyperliquidity'] = no_hyperliquidity
    action: GenesisAction = {'type': 'spotDeploy', 'genesis': sub_action}
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
