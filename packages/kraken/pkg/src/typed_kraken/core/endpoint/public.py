"""Request serialization shared by Kraken's public Futures and chart endpoints."""

from dataclasses import dataclass
from types import UnionType
from typing_extensions import Any, Mapping, Protocol, Self, TypeVar, cast
from urllib.parse import quote
import json
import re

from typed_core.validation import validator

T = TypeVar('T')


class PublicClient(Protocol):
  """Transport contract for unsigned public HTTP requests."""

  async def request(
    self,
    path: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one public GET request and validate its response."""
    ...

  async def __aenter__(self) -> Self:
    """Acquire the transport."""
    ...

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the transport."""
    ...


@dataclass(frozen=True, kw_only=True)
class PublicEndpoint:
  """Base for public Futures REST and chart request/reply endpoints."""

  client: PublicClient

  async def __aenter__(self) -> Self:
    """Acquire the endpoint's transport."""
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the endpoint's transport."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    meta: Mapping[str, Any] | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Serialize timestamps and substitute path fields before sending the query.

    Args:
      request: Typed endpoint parameters.
      method: Public HTTP method; only GET is supported.
      path: API path, optionally containing named placeholders.
      meta: Endpoint metadata; these public endpoints require none.
      validate: Override response validation for this call.
      request_type: Parameter schema used for wire serialization.
      response_type: Response schema used for validation.
    """
    if method != 'GET':
      raise ValueError('Public Futures and chart endpoints support GET only')
    values: dict[str, Any] = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request is not None and request_type is not None
      else {}
    )
    for name in re.findall(r'{(\w+)}', path):
      path = path.replace('{' + name + '}', quote(str(values.pop(name)), safe=''))
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    return await self.client.request(
      path, values or None, validator=response_validator, validate=validate
    )
