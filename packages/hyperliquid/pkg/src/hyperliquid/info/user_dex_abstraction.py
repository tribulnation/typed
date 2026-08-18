from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class UserDexAbstractionAction(TypedDict):
  type: Literal['userDexAbstraction']
  user: str


adapter = pydantic.TypeAdapter(bool | None)


class UserDexAbstraction(InfoMixin):
  async def user_dex_abstraction(self, *, user: str) -> bool | None:
    """Query whether a user's HIP-3 (builder-deployed) perp dex balances are abstracted into their primary account state, through Hyperliquid POST /info using request type `userDexAbstraction`.

    Args:
      user: User address in 42-character hexadecimal format, e.g. 0x0000000000000000000000000000000000000000.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint#query-a-users-hip-3-dex-abstraction-state)
    """
    params: UserDexAbstractionAction = {
      'type': 'userDexAbstraction',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
