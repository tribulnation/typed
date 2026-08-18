from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class DelegatorReward(TypedDict):
  """A single staking-reward event."""

  source: Literal['commission', 'delegation']
  """Where this reward came from: `delegation` for rewards earned on delegated HYPE, `commission` for a validator's cut of its delegators' rewards."""
  time: int
  """Reward time, in milliseconds since epoch."""
  totalAmount: str
  """Reward amount, as a decimal string."""


class StakingRewardsAction(TypedDict):
  type: Literal['delegatorRewards']
  user: str


adapter = pydantic.TypeAdapter(list[DelegatorReward])


class StakingRewards(InfoMixin):
  async def staking_rewards(self, *, user: str) -> list[DelegatorReward]:
    """Query a user's history of staking rewards -- both delegation rewards and validator commission -- through Hyperliquid POST /info using request type `delegatorRewards`.

    Args:
      user: Address to query staking rewards for, in 42-character hexadecimal format.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: StakingRewardsAction = {
      'type': 'delegatorRewards',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
