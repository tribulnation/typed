from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SubAccountOptionsEnabled(TypedDict):
  """Options-enablement result."""

  email: NotRequired[str]
  """Sub-account email."""
  isEOptionsEnabled: NotRequired[bool]
  """Whether Options trading is now enabled for the sub-account."""


class EnableOptions(RpcEndpoint):
  """Enable Options (EAPI) trading for a sub-account, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    validate: bool | None = None,
  ) -> SubAccountOptionsEnabled:
    """Enable Options (EAPI) trading for a sub-account, for the master account.

    Args:
      email: Sub-account email.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/account-management#enable-options-for-sub-account)
    """
    params: dict = {
      'email': email,
    }
    _Response = SubAccountOptionsEnabled
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/sub-account/eoptions/enable',
      params=params,
      validator=_validator,
      validate=validate,
    )
