from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class UserVaultEquitiesAction(TypedDict):
  type: Literal['userVaultEquities']
  user: str


class UserVaultEquity(TypedDict):
  """A user's deposit into a single vault."""

  equity: str
  """The user's current equity in the vault, as a decimal string."""
  vaultAddress: str
  """Address of the vault, in 42-character hexadecimal format."""


adapter = pydantic.TypeAdapter(list[UserVaultEquity])


class UserVaultEquities(InfoMixin):
  async def user_vault_equities(self, *, user: str) -> list[UserVaultEquity]:
    """Retrieve every vault a user has equity in, and the current equity held in each, through Hyperliquid POST /info using request type `userVaultEquities`.

    Args:
      user: Address to query vault deposits for, in 42-character hexadecimal format.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: UserVaultEquitiesAction = {
      'type': 'userVaultEquities',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
