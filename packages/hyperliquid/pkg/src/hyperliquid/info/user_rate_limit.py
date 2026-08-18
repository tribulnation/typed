from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class UserRateLimitAction(TypedDict):
  type: Literal['userRateLimit']
  user: str


class UserRateLimitResponse(TypedDict):
  """A user's `/exchange` rate-limit usage."""

  cumVlm: str
  """Cumulative trading volume (USD) backing this user's request budget, as an unbounded decimal string."""
  nRequestsUsed: int
  """Requests used in the current window: `max(0, cumulative requests used - reserved requests)`."""
  nRequestsCap: int
  """Total request budget for the current window."""
  nRequestsSurplus: int
  """Unused reserved requests carried over: `max(0, reserved requests - cumulative requests used)`."""


adapter = pydantic.TypeAdapter(UserRateLimitResponse)


class UserRateLimit(InfoMixin):
  async def user_rate_limit(self, *, user: str) -> UserRateLimitResponse:
    """Retrieve a user's Hyperliquid `/exchange` rate-limit usage: the cumulative trading volume that backs their request budget, how many requests they have used, their total request cap, and any unused reserved requests carried over as surplus.

    Args:
      user: Address to look up, as a 42-character hexadecimal string.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: UserRateLimitAction = {
      'type': 'userRateLimit',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
