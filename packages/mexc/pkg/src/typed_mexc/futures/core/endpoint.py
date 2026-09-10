"""Base endpoint class for MEXC Futures' HTTP endpoints: design §2's single
`request()` verb, deciding signed-vs-public purely from `meta['signed']`. `core`
decides everything about wire mechanics (design §2) -- including, here, substituting
any `{placeholder}` in `path` from the flat `Request` it's handed (design §7:
"location markers are eliminated, not redeclared" -- a property whose name matches a
template placeholder is a path parameter, resolved by `core` alone, never a codegen-side
split).
"""

from typing_extensions import Any, NotRequired, Protocol, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json
import re

from typed_core.validation import validator

T = TypeVar('T')

PLACEHOLDER = re.compile(r'\{([^{}]+)\}')
"""A `{name}` template slot inside `path` -- the identical rule `spec/request.py`'s
own `PLACEHOLDER` uses for the same purpose at codegen/mock-serving time."""


class Meta(TypedDict):
  """`futures_http`'s own `meta` shape (`codegen/config.toml` `[cores.futures_http].meta`):
  whether this call needs HMAC-SHA256 signing. Hand-written to match that declared
  JSON Schema -- never code-generated (design §2/§6, the same precedent this repo
  already uses for a spec-declared timestamp `format`; S27)."""

  signed: NotRequired[bool]
  """Whether this call needs signing (absent/`False` for a public endpoint)."""


class RpcClient(Protocol):
  """Structural interface `FuturesHttpClient` implements to back a
  `FuturesHttpEndpoint`."""

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
class FuturesHttpEndpoint:
  """Base class for every MEXC Futures HTTP endpoint -- the resolved `futures_http`
  core for the whole `futures/http/` subtree (`codegen/config.toml`)."""

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
    """Perform one Futures REST call (design §2's single verb): serialize `request`
    through `request_type`'s validator (ADR 0020/S28) into a plain, wire-ready dict,
    substitute every `{placeholder}` in `path` from it, and send whatever's left
    unsigned (public) or signed (`meta['signed']`).

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire path, e.g. `/api/v1/contract/depth/{symbol}`.
      meta: This call's own quirks -- whether it needs signing.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    values: dict[str, Any] = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else {}
    )
    for name in PLACEHOLDER.findall(path):
      if name in values:
        path = path.replace('{' + name + '}', str(values.pop(name)))
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = self.client.authed_request if meta.get('signed', False) else self.client.request
    return await call(method, path, values or None, validator=response_validator, validate=validate)
