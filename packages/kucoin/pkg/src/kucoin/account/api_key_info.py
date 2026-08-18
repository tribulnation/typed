"""`GET /api/v1/user/api-key` — Get Apikey Info."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class ApiKeyInfo(TypedDict):
  """Metadata for the API key that signed the request."""

  remark: str
  """The API key's remark/label, set at creation time."""
  apiKey: str
  """The API key itself."""
  apiVersion: int
  """API key version."""
  permission: str
  """Comma-separated list of permission scopes granted to the key, e.g. `General,Spot,Margin,Futures,InnerTransfer,Transfer,Earn`."""
  ipWhitelist: NotRequired[str]
  """Comma-separated IP whitelist configured for the key, if any."""
  createdAt: int
  """Unix milliseconds when the key was created."""
  uid: int
  """Account UID the key belongs to."""
  isMaster: bool
  """Whether this is a master account's key (as opposed to a sub-account's)."""
  region: NotRequired[str]
  """Geographic region associated with the account."""
  kycStatus: NotRequired[int]
  """KYC verification level."""
  siteType: NotRequired[str]
  """Platform/site the account is registered under, e.g. `global`."""
  subName: NotRequired[str]
  """Sub-account name the key belongs to. Absent for a master account's key."""


_Type = ApiKeyInfo
adapter = validator[_Type](_Type)  # type: ignore


class ApiKeyInfoEndpoint(RpcEndpoint):
  """`Get Apikey Info` — mixed into `Account`, the product exposing `account.api_key_info`."""

  async def api_key_info(self, *, validate: bool | None = None) -> ApiKeyInfo:
    """Get metadata for the API key used to authenticate this request. Works for both master and sub-user API keys.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'GET',
      '/api/v1/user/api-key',
      validator=adapter,
      validate=validate,
    )
