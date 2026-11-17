"""Base endpoint class for the REST v2 market-data APIs (gateway and archive): plain `GET`s
answered with bare JSON."""

from typing_extensions import Any, Mapping, Protocol, Self, TypeVar
from dataclasses import dataclass
from types import UnionType

from typed_core.validation import validator

from .wire import dump_request

T = TypeVar('T')


class RestClient(Protocol):
  """Structural interface the REST v2 transport implements to back a `RestEndpoint`."""

  async def get(
    self,
    path: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """`GET` one path below the v2 base, map errors, then validate.

    Args:
      path: Path below the v2 base (`/assets`).
      params: Query string values.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    ...


@dataclass(kw_only=True, frozen=True)
class RestEndpoint:
  """Base class for REST v2 endpoints."""

  client: RestClient
  """The gateway v2 or archive v2 transport."""

  async def __aenter__(self) -> Self:
    """Return this surface. Nothing opens: transports connect lazily, on first use."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client (`core.base.ClientBase`) closes transports."""

  async def request(
    self,
    request: Any = None,
    *,
    method: str = 'GET',
    path: str,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one REST v2 call: every request field goes in the query string.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: Always `GET`: the v2 APIs serve nothing else.
      path: Path below the v2 base.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return await self.client.get(
      path, values or None, validator=response_validator, validate=validate
    )
