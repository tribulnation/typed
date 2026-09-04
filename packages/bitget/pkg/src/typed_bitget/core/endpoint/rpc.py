"""Base endpoint class for Bitget's HTTP endpoints -- the resolved "rest" core
(`codegen/config.toml`), shared identically by Classic v2 and UTA v3 (`spec/core.md` Surfaces:
"one connection pool, one set of credentials, one envelope, one error map"). Design §2's
single `request()` verb, deciding public-vs-signed purely from `meta['required']` and
query-string-vs-JSON-body purely from the wire HTTP method -- every real Bitget REST
endpoint sends a `GET` as a query string and anything else as a JSON body, confirmed
against the live spec (352 `GET`s all query-shaped, 161 non-`GET`s all body-shaped bar
one parameterless `POST`).
"""

from typing_extensions import Any, NotRequired, Protocol, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.validation import validator

T = TypeVar('T')


class Meta(TypedDict):
  """`rest`'s own `meta` shape (`codegen/config.toml` `[cores.rest].meta`): whether this call
  needs HMAC-SHA256 signing. Hand-written to match that declared JSON Schema -- never
  code-generated (design §2/§6, the same precedent this repo already uses for a
  spec-declared timestamp `format`; S27)."""

  required: NotRequired[bool]
  """Whether this call needs signing (absent/`False` for every public endpoint)."""


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T: ...

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    ...

  async def __aenter__(self) -> Self: ...
  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for every Bitget REST endpoint -- the resolved "rest" core for both
  Classic v2 and UTA v3 (`codegen/config.toml`)."""

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
    """Perform one REST call (design §2's single verb): serialize `request` through
    `request_type`'s validator (ADR 0020/S28) into a plain, wire-ready dict, send it as a
    query string (`GET`) or JSON body (anything else) -- signed when `meta['required']`,
    unsigned otherwise -- and validate the unwrapped `data` payload through
    `response_type`'s validator.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb -- decides query-string (`GET`) vs JSON-body (anything else)
        placement.
      path: Wire path, e.g. `/api/v2/spot/public/symbols`.
      meta: This call's own quirks -- whether it needs HMAC-SHA256 signing.
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
    call = self.client.authed_request if meta.get('required', False) else self.client.request
    kwargs = {'params': values} if method == 'GET' else {'json': values}
    return await call(method, path, validator=response_validator, validate=validate, **kwargs)
