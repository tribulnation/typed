from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class WithdrawQuota(TypedDict):
  """The account's 24-hour withdrawal quota, denominated in BTC."""

  wdQuota: str
  """Total withdrawal quota available, denominated in BTC."""
  usedWdQuota: str
  """Amount of the withdrawal quota already used, denominated in BTC."""


class Quota(RpcEndpoint):
  """Fetch the account's total and used 24-hour withdrawal quota, denominated in BTC."""

  async def quota(self, *, validate: bool | None = None) -> WithdrawQuota:
    """Fetch the account's total and used 24-hour withdrawal quota, denominated in BTC.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#fetch-withdraw-quota)
    """
    _Response = WithdrawQuota
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/capital/withdraw/quota', validator=_validator, validate=validate
    )
