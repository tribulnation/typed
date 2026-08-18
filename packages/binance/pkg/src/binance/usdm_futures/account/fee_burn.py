from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UsdMFuturesFeeBurnStatus(TypedDict):
  """BNB fee discount status for this account."""

  feeBurn: NotRequired[bool]
  """Whether the BNB fee discount is enabled."""


class FeeBurn(RpcEndpoint):
  """Get this account's BNB fee discount status (fee discount on or off)."""

  async def fee_burn(self, *, validate: bool | None = None) -> UsdMFuturesFeeBurnStatus:
    """Get this account's BNB fee discount status (fee discount on or off).

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-bnb-burn-status)
    """
    _Response = UsdMFuturesFeeBurnStatus
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/fapi/v1/feeBurn', validator=_validator, validate=validate
    )
