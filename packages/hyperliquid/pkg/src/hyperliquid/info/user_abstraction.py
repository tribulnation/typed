from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class UserAbstractionAction(TypedDict):
  type: Literal['userAbstraction']
  user: str


adapter = pydantic.TypeAdapter(
  Literal['unifiedAccount', 'portfolioMargin', 'disabled', 'default', 'dexAbstraction']
)


class UserAbstraction(InfoMixin):
  async def user_abstraction(
    self,
    *,
    user: str,
  ) -> Literal[
    'unifiedAccount', 'portfolioMargin', 'disabled', 'default', 'dexAbstraction'
  ]:
    """Query a user's account abstraction state, through Hyperliquid POST /info using request type `userAbstraction`. Abstraction state controls how the user's margin and balances are aggregated across accounts and perp dexes.

    Args:
      user: User address in 42-character hexadecimal format, e.g. 0x0000000000000000000000000000000000000000.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint#query-a-users-abstraction-state)
    """
    params: UserAbstractionAction = {
      'type': 'userAbstraction',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
