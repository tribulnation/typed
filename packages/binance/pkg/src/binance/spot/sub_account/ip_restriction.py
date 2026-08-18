from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SubAccountApiKeyIpRestriction(TypedDict):
  """The API key's current IP restriction."""

  ipRestrict: NotRequired[str]
  """Whether IP restriction is enabled (`"true"`/`"false"`)."""
  ipList: NotRequired[list[str]]
  """Trusted IP addresses on the list."""
  updateTime: NotRequired[int]
  """Time the restriction was last updated."""
  apiKey: NotRequired[str]
  """Sub-account API key the restriction applies to."""


class IpRestriction(RpcEndpoint):
  """Get the IP restriction for a sub-account API key, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    sub_account_api_key: str,
    validate: bool | None = None,
  ) -> SubAccountApiKeyIpRestriction:
    """Get the IP restriction for a sub-account API key, for the master account.

    Args:
      email: Sub-account email.
      sub_account_api_key: Sub-account API key.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#get-ip-restriction-for-asub-account-api-key)
    """
    params: dict = {
      'email': email,
      'subAccountApiKey': sub_account_api_key,
    }
    _Response = SubAccountApiKeyIpRestriction
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/subAccountApi/ipRestriction',
      params=params,
      validator=_validator,
      validate=validate,
    )
