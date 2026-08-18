from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class UserRoleAction(TypedDict):
  type: Literal['userRole']
  user: str


class UserRoleAgentData(TypedDict):
  """Identifies the account an API agent wallet acts on behalf of."""

  user: str
  """Address of the account this API agent trades on behalf of."""


class UserRoleMissing(TypedDict):
  """An address Hyperliquid has no role record for."""

  role: Literal['missing']
  """Role discriminator: `missing`."""


class UserRoleSubAccountData(TypedDict):
  """Identifies the master account a subaccount belongs to."""

  master: str
  """Address of the master account this subaccount belongs to."""


class UserRoleUser(TypedDict):
  """An ordinary trading account."""

  role: Literal['user']
  """Role discriminator: `user`."""


class UserRoleVault(TypedDict):
  """A vault address."""

  role: Literal['vault']
  """Role discriminator: `vault`."""


class UserRoleAgent(TypedDict):
  """An API agent wallet approved to trade on behalf of another account."""

  role: Literal['agent']
  """Role discriminator: `agent`."""
  data: UserRoleAgentData


class UserRoleSubAccount(TypedDict):
  """A subaccount address."""

  role: Literal['subAccount']
  """Role discriminator: `subAccount`."""
  data: UserRoleSubAccountData


adapter = pydantic.TypeAdapter(
  UserRoleUser | UserRoleAgent | UserRoleVault | UserRoleSubAccount | UserRoleMissing
)


class UserRole(InfoMixin):
  async def user_role(
    self,
    *,
    user: str,
  ) -> (
    UserRoleUser | UserRoleAgent | UserRoleVault | UserRoleSubAccount | UserRoleMissing
  ):
    """Determine a user's role on Hyperliquid: an ordinary trading account, an API agent wallet, a vault, a subaccount, or an address Hyperliquid has no record of.

    Args:
      user: Address to look up, as a 42-character hexadecimal string.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: UserRoleAction = {
      'type': 'userRole',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
