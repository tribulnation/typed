"""`GET /api/v1/status` — Get Service Status."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class ServiceStatus(TypedDict):
  """Current service status."""

  status: str
  """Service status; `open` when fully operational. Docs mention this value but don't publish the closed set of alternatives (e.g. maintenance states) — left bare rather than guessing, per rule 2."""
  msg: str
  """Status message, typically empty when operational."""


_Type = ServiceStatus
adapter = validator[_Type](_Type)  # type: ignore


class ServiceStatusEndpoint(RpcEndpoint):
  """`Get Service Status` — mixed into `Spot`, the product exposing `spot.service_status`."""

  async def service_status(self, *, validate: bool | None = None) -> ServiceStatus:
    """Get KuCoin's current service status.

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
