"""`GET /api/v1/status` — Get Service Status."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesServiceStatus(TypedDict):
  """Current futures service status."""

  status: str
  """Service status; `open` when fully operational. Docs mention this value but not the closed set of alternatives (e.g. a maintenance state) -- left bare per rule 2, same as `spot.service_status`."""
  msg: str
  """Status message, typically empty when operational."""


_Type = FuturesServiceStatus
adapter = validator[_Type](_Type)  # type: ignore


class ServiceStatus(RpcEndpoint):
  """`Get Service Status` — mixed into `Futures`, the product exposing `futures.service_status`."""

  async def service_status(
    self, *, validate: bool | None = None
  ) -> FuturesServiceStatus:
    """Get KuCoin Futures' current service status.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.request(
      'GET',
      '/api/v1/status',
      validator=adapter,
      validate=validate,
    )
