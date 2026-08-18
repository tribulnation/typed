from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Any, Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class V3balance(TypedDict):
  """Available balance in the account."""

  value: str
  """Balance amount, as a decimal string."""
  currency: str
  """Currency code of `value`."""


class V3account(TypedDict):
  """An Advanced Trade brokerage account."""

  uuid: str
  """Unique identifier for account."""
  name: str
  """Name for the account."""
  currency: str
  """Currency symbol for the account."""
  available_balance: V3balance
  default: bool
  """Whether or not this account is the user's primary account."""
  active: bool
  """Whether or not this account is active and okay to use."""
  created_at: str
  """Time at which this account was created, RFC 3339."""
  updated_at: str
  """Time at which this account was updated, RFC 3339."""
  deleted_at: NotRequired[str | None]
  """Time at which this account was deleted, RFC 3339, or null if not deleted."""
  type: Literal[
    'ACCOUNT_TYPE_UNSPECIFIED',
    'ACCOUNT_TYPE_CRYPTO',
    'ACCOUNT_TYPE_FIAT',
    'ACCOUNT_TYPE_VAULT',
    'ACCOUNT_TYPE_PERP_FUTURES',
  ]
  """Account type defines the type of account that is supported."""
  ready: bool
  """Whether or not this account is ready to trade."""
  hold: dict[str, Any]
  """Amount that is being held for pending transfers against the available balance."""
  retail_portfolio_id: str
  """The ID of the portfolio this account is associated with."""
  platform: Literal[
    'ACCOUNT_PLATFORM_UNSPECIFIED',
    'ACCOUNT_PLATFORM_CONSUMER',
    'ACCOUNT_PLATFORM_CFM_CONSUMER',
    'ACCOUNT_PLATFORM_INTX',
  ]
  """Platform indicates if the account is for spot (CONSUMER), US Derivatives (CFM_CONSUMER), or International Exchange (INTX)."""


class V3accountResponse(TypedDict):
  account: V3account


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /api/v3/brokerage/accounts/{account_uuid}`."""

  async def get(self, account_uuid: str) -> V3accountResponse:
    """Get a single Advanced Trade v3 brokerage account by UUID.

    Args:
      account_uuid: The account's UUID.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/accounts/get-account)
    """
    return await self.authed_request(
      'GET',
      f'/api/v3/brokerage/accounts/{account_uuid}',
      validator=validator(V3accountResponse),
    )
