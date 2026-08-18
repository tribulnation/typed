"""`public/hello` — `public/hello`."""

from typing_extensions import TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class HelloResult(TypedDict):
  """Deribit's own API version, returned in reply to the client's introduction."""

  version: str
  """Deribit's own API version."""


validate_hello = validator[HelloResult](HelloResult)


class Hello(RpcEndpoint):
  """`public/hello`."""

  async def hello(
    self,
    *,
    client_name: str,
    client_version: str,
    validate: bool | None = None,
  ) -> HelloResult:
    """Introduces the client software connected to the Deribit platform over WebSocket. The supplied data may affect the maintained connection and is collected for internal statistical purposes. Deribit responds by introducing itself, returning its own API version.

    Args:
      client_name: Client software name.
      client_version: Client software version.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/supporting/public-hello)
    """
    params: dict = {
      'client_name': client_name,
      'client_version': client_version,
    }
    return await self.request(
      'public/hello', params=params, validator=validate_hello, validate=validate
    )
