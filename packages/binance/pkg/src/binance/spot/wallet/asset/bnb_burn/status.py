from typed_core.validation import validator
from binance.types import BnbBurnStatus
from binance.core.endpoint.rpc import RpcEndpoint


class Status(RpcEndpoint):
  """Fetch whether BNB Burn is enabled for Spot trading fees and Margin loan interest."""

  async def status(self, *, validate: bool | None = None) -> BnbBurnStatus:
    """Fetch whether BNB Burn is enabled for Spot trading fees and Margin loan interest.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#toggle-bnb-burn-on-spot-trade-and-margin-interest)
    """
    _Response = BnbBurnStatus
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/bnbBurn', validator=_validator, validate=validate
    )
