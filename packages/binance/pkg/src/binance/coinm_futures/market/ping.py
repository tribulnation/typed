from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class Response200(TypedDict):
  """Always empty on success."""


class Ping(RpcEndpoint):
  """Test connectivity to the COIN-M Futures REST API."""

  async def ping(self, *, validate: bool | None = None) -> Response200:
    """Test connectivity to the COIN-M Futures REST API.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#test-connectivity)
    """
    _Response = Response200
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/dapi/v1/ping', validator=_validator, validate=validate
    )
