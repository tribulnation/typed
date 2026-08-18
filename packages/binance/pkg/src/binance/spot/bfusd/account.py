from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BfusdAccountSummary(TypedDict):
  """This account's BFUSD holdings and profit."""

  bfusdAmount: NotRequired[str]
  """Amount of BFUSD held, as a decimal string."""
  usdtProfit: NotRequired[str]
  """Cumulative profit denominated in USDT, as a decimal string."""
  bfusdProfit: NotRequired[str]
  """Cumulative profit denominated in BFUSD, as a decimal string."""


class Account(RpcEndpoint):
  """Get this account's BFUSD account information."""

  async def __call__(self, *, validate: bool | None = None) -> BfusdAccountSummary:
    """Get this account's BFUSD account information.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#get-bfusd-account)
    """
    _Response = BfusdAccountSummary
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/bfusd/account', validator=_validator, validate=validate
    )
