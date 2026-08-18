from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class AccountStatus(TypedDict):
  """Wrapper carrying the account's status."""

  data: str
  """Account status, e.g. "Normal"."""


class Status(RpcEndpoint):
  """Fetch account status detail, e.g. whether the account is in normal standing."""

  async def status(self, *, validate: bool | None = None) -> AccountStatus:
    """Fetch account status detail, e.g. whether the account is in normal standing.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#account-status)
    """
    _Response = AccountStatus
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/account/status', validator=_validator, validate=validate
    )
