from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class ClaimRewardsAction(TypedDict):
  type: Literal['claimRewards']


class ClaimRewardsResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[ClaimRewardsResult])


class ClaimRewards(ExchangeMixin):
  async def claim_rewards(
    self,
    *,
    expires_after: int | None = None,
  ) -> ExchangeResponse[ClaimRewardsResult]:
    """Claim the caller's accrued rewards, through Hyperliquid POST /exchange using the L1 `claimRewards` action.

    Args:
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: ClaimRewardsAction = {
      'type': 'claimRewards',
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
