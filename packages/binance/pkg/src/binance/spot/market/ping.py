from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class Response200(TypedDict):
  """Always empty on success."""


class Ping(RpcEndpoint):
  """Test connectivity"""

  async def ping(self, *, validate: bool | None = None) -> Response200:
    """Test connectivity to the REST API.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#test-connectivity)
    """
    _Response = Response200
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/api/v3/ping', validator=_validator, validate=validate
    )
