from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class DelegatorHistoryDelegateDelta(TypedDict):
  """A single delegate/undelegate change against one validator."""

  amount: str
  """Amount of HYPE delegated or undelegated in this event, as a decimal string."""
  isUndelegate: bool
  """True when this event removed a delegation, false when it added one."""
  validator: str
  """Address of the validator this event's delegation change applies to, in 42-character hexadecimal format."""


class StakingHistoryAction(TypedDict):
  type: Literal['delegatorHistory']
  user: str


class DelegatorHistoryDelta(TypedDict):
  """The delegation change this event recorded."""

  delegate: DelegatorHistoryDelegateDelta


class DelegatorHistoryEvent(TypedDict):
  """A single staking-delegation event in a user's history."""

  delta: DelegatorHistoryDelta
  hash: str
  """Transaction hash of the on-chain action that produced this event."""
  time: int
  """Event time, in milliseconds since epoch."""


adapter = pydantic.TypeAdapter(list[DelegatorHistoryEvent])


class StakingHistory(InfoMixin):
  async def staking_history(self, *, user: str) -> list[DelegatorHistoryEvent]:
    """Query a user's history of staking-delegation events, through Hyperliquid POST /info using request type `delegatorHistory`.

    Args:
      user: Address to query staking history for, in 42-character hexadecimal format.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: StakingHistoryAction = {
      'type': 'delegatorHistory',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
