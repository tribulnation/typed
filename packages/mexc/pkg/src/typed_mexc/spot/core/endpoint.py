"""Base endpoint class for MEXC Spot's HTTP endpoints: design §2's single `request()`
verb, deciding signed-vs-public purely from `meta['signed']`. `core` decides everything
about wire mechanics (design §2) -- here, that every signed call is a query string,
never a JSON body.
"""

from typing_extensions import Any, NotRequired, Protocol, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.validation import validator

T = TypeVar('T')


class Meta(TypedDict):
  """`spot_http`'s own `meta` shape (`codegen/config.toml` `[cores.spot_http].meta`): whether
  this call needs HMAC-SHA256 query-string signing. Hand-written to match that declared
  JSON Schema -- never code-generated (design §2/§6, the same precedent this repo
  already uses for a spec-declared timestamp `format`; S27)."""

  signed: NotRequired[bool]
  """Whether this call needs signing (absent/`False` for a public endpoint)."""


class RpcClient(Protocol):
  """Structural interface `SpotHttpClient` implements to back a `SpotHttpEndpoint`."""

  async def request(
    self, method: str, path: str, params: dict[str, Any] | None = None, *,
    validator: 'validator[T] | None' = None, validate: bool | None = None,
  ) -> T:
    """Send an unsigned request to a public endpoint."""
    ...

  async def authed_request(
    self, method: str, path: str, params: dict[str, Any] | None = None, *,
    validator: 'validator[T] | None' = None, validate: bool | None = None,
  ) -> T:
    """Sign and send a request to a private endpoint."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class SpotHttpEndpoint:
  """Base class for every MEXC Spot HTTP endpoint -- the resolved `spot_http` core for
  the whole `spot/http/` subtree (`codegen/config.toml`)."""

  client: RpcClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one Spot REST call (design §2's single verb): serialize `request`
    through `request_type`'s validator (ADR 0020/S28) into a plain, wire-ready dict,
    and send it unsigned (public) or signed (`meta['signed']`) -- `path` never carries
    a `{placeholder}`, so no path-templating is needed here (unlike futures).

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire path, e.g. `/api/v3/order`.
      meta: This call's own quirks -- whether it needs signing.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    values = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = self.client.authed_request if meta.get('signed', False) else self.client.request
    return await call(method, path, values, validator=response_validator, validate=validate)
