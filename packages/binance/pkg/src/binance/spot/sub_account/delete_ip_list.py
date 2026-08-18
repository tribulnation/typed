from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SubAccountApiKeyIpRestriction(TypedDict):
  """The API key's updated IP restriction."""

  ipRestrict: NotRequired[str]
  """Whether IP restriction is enabled (`"true"`/`"false"`)."""
  ipList: NotRequired[list[str]]
  """Trusted IP addresses remaining on the list."""
  updateTime: NotRequired[int]
  """Time the restriction was last updated."""
  apiKey: NotRequired[str]
  """Sub-account API key the restriction applies to."""


class DeleteIpList(RpcEndpoint):
  """Delete IP addresses from a sub-account API key's trusted-IP restriction list, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    sub_account_api_key: str,
    ip_address: str,
    validate: bool | None = None,
  ) -> SubAccountApiKeyIpRestriction:
    """Delete IP addresses from a sub-account API key's trusted-IP restriction list, for the master account.

    Args:
      email: Sub-account email.
      sub_account_api_key: Sub-account API key.
      ip_address: IP addresses to remove, comma-separated. Can be sent in batches.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#delete-ip-list-for-asub-account-api-key)
    """
    params: dict = {
      'email': email,
      'subAccountApiKey': sub_account_api_key,
      'ipAddress': ip_address,
    }
    _Response = SubAccountApiKeyIpRestriction
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/sapi/v1/sub-account/subAccountApi/ipRestriction/ipList',
      params=params,
      validator=_validator,
      validate=validate,
    )
