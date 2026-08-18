from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class Response200(TypedDict):
  """Always empty on success."""


class Ping(RpcEndpoint):
  """Test Connectivity"""

  async def ping(self, *, validate: bool | None = None) -> Response200:
    """Test connectivity to the REST API.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/market-data#test-connectivity)
    """
    _Response = Response200
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/papi/v1/ping', validator=_validator, validate=validate
    )
