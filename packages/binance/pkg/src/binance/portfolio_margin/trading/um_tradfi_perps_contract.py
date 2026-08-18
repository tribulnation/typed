from typing_extensions import Any
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UmTradfiPerpsContract(RpcEndpoint):
  """Futures TradFi Perps Contract"""

  async def um_tradfi_perps_contract(
    self,
    *,
    validate: bool | None = None,
  ) -> dict[str, Any]:
    """Sign TradFi-Perps agreement contract.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#futures-tradfi-perps-contract)
    """
    _Response = dict[str, Any]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST', '/papi/v1/um/stock/contract', validator=_validator, validate=validate
    )
