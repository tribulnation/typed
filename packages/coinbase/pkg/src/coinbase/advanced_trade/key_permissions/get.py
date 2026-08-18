from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class KeyPermissions(TypedDict):
  """The calling CDP API Key's permissions and portfolio scope."""

  can_view: bool
  """Whether the key has view permissions."""
  can_trade: bool
  """Whether the key has trade permissions."""
  can_transfer: bool
  """Whether the key has deposit/withdrawal permissions."""
  portfolio_uuid: str
  """The id of the portfolio the key is scoped to."""
  portfolio_type: Literal['UNDEFINED', 'DEFAULT', 'CONSUMER', 'INTX']
  """The type of portfolio the key is scoped to."""


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /api/v3/brokerage/key_permissions`."""

  async def get(self) -> KeyPermissions:
    """Get the permissions and portfolio scoping of the calling CDP API Key.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/data-api/get-api-key-permissions)
    """
    return await self.authed_request(
      'GET', '/api/v3/brokerage/key_permissions', validator=validator(KeyPermissions)
    )
