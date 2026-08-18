from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BrokerSubAccountApiIpRestriction(TypedDict):
  """This sub-account API key's IP restriction."""

  subaccountId: str
  """Sub-account identifier."""
  ipRestrict: bool
  """Whether this API key is restricted to the listed IPs."""
  apikey: str
  """API key this restriction applies to."""
  ipList: list[str]
  """Whitelisted IP addresses."""
  updateTime: Timestamp
  """Time this restriction was last updated."""


class SubAccountApiIpRestriction(RpcEndpoint):
  """Get IP Restriction for Sub Account Api Key"""

  async def sub_account_api_ip_restriction(
    self,
    *,
    sub_account_id: str,
    sub_account_api_key: str,
    validate: bool | None = None,
  ) -> BrokerSubAccountApiIpRestriction:
    """Get a sub-account API key's IP whitelist.

    Args:
      sub_account_id: Sub-account identifier.
      sub_account_api_key: Sub-account API key.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params: dict = {
      'subAccountId': sub_account_id,
      'subAccountApiKey': sub_account_api_key,
    }
    _Response = BrokerSubAccountApiIpRestriction
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/broker/subAccountApi/ipRestriction',
      params=params,
      validator=_validator,
      validate=validate,
    )
