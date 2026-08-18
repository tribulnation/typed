from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class Delegation(TypedDict):
  """A user's delegation to a single validator."""

  amount: str
  """Amount of HYPE delegated to this validator, as a decimal string."""
  lockedUntilTimestamp: int
  """Time this delegation is locked until, in milliseconds since epoch. Undelegating before this time is not allowed."""
  validator: str
  """Address of the validator this amount is delegated to, in 42-character hexadecimal format."""


class StakingDelegationsAction(TypedDict):
  type: Literal['delegations']
  user: str


adapter = pydantic.TypeAdapter(list[Delegation])


class StakingDelegations(InfoMixin):
  async def staking_delegations(self, *, user: str) -> list[Delegation]:
    """Query the validators a user currently has HYPE delegated to, through Hyperliquid POST /info using request type `delegations`.

    Args:
      user: Address to query delegations for, in 42-character hexadecimal format.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: StakingDelegationsAction = {
      'type': 'delegations',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
