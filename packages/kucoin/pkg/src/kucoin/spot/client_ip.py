"""`GET /api/v1/my-ip` — Get Client IP Address."""

from typed_core.validation import validator
from kucoin.core import RpcEndpoint


_Type = str
adapter = validator[_Type](_Type)  # type: ignore


class ClientIp(RpcEndpoint):
  """`Get Client IP Address` — mixed into `Spot`, the product exposing `spot.client_ip`."""

  async def client_ip(self, *, validate: bool | None = None) -> str:
    """Get the caller's IP address as seen by KuCoin's API servers.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.request(
      'GET',
      '/api/v1/my-ip',
      validator=adapter,
      validate=validate,
    )
