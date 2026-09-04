"""`GET /api/v2/user-info` — Get Account Summary Info."""

from typed_core.validation import TypedDict, validator
from typed_kucoin.core.endpoint.rpc import RpcEndpoint


class UserInfoResult(TypedDict):
  """Authenticated account's VIP level and sub-account quotas."""

  level: int
  """User VIP level."""
  subQuantity: int
  """Number of sub-accounts."""
  spotSubQuantity: int
  """Number of sub-accounts with spot trading permission enabled."""
  marginSubQuantity: int
  """Number of sub-accounts with margin trading permission enabled."""
  futuresSubQuantity: int
  """Number of sub-accounts with futures trading permission enabled."""
  optionSubQuantity: int
  """Number of sub-accounts with option trading permission enabled."""
  maxSubQuantity: int
  """Max. number of sub-accounts (`maxDefaultSubQuantity + maxSpotSubQuantity`)."""
  maxDefaultSubQuantity: int
  """Max. number of default open sub-accounts, per VIP level."""
  maxSpotSubQuantity: int
  """Max. number of sub-accounts with additional spot trading permission."""
  maxMarginSubQuantity: int
  """Max. number of sub-accounts with additional margin trading permission."""
  maxFuturesSubQuantity: int
  """Max. number of sub-accounts with additional futures trading permission."""
  maxOptionSubQuantity: int
  """Max. number of sub-accounts with additional option trading permission."""


adapter = validator(UserInfoResult)


class UserInfo(RpcEndpoint):
  """`Get Account Summary Info` — mixed into `Account`, the product exposing
  `account.user_info`."""

  async def user_info(self, *, validate: bool | None = None) -> UserInfoResult:
    """Get the authenticated account's VIP level and sub-account quotas.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.client.authed_request(
      'GET', '/api/v2/user-info', validator=adapter, validate=validate
    )
