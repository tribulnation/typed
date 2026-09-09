"""Base endpoint class for KuCoin REST endpoints: design §2's single `request()` verb,
deciding public-vs-signed purely from `meta['signed']`, and routing `x-tenant` (KuCoin's
only declared `in: 'header'` parameter, `broker.rebate_download_v3`) to a real HTTP
header instead of a query/body field -- the same fold binance's `lang` uses, since the
new `request` shape drops the `header` role marker entirely (design §7).

Every Classic product -- Account, Spot, Margin, Earn, VIP Lending, Convert, Affiliate,
Futures, Copy Trading, Broker -- mixes its generated methods onto a subclass of this one
class, rooted at whichever of the three base URLs its product needs (`core/base.py`).
"""

from typing_extensions import Any, Mapping, NotRequired, Protocol, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.validation import validator

from .wire import substitute_template

T = TypeVar('T')

HEADER_FIELD = 'x-tenant'
"""The one wire field KuCoin sends as a real HTTP header rather than a query/body field
-- `broker.rebate_download_v3`'s broker tenant name. Popped out of the serialized
`request` dict and routed to `headers`, never left in `params`/`json`."""


class Meta(TypedDict):
  """`default`'s own `meta` shape (`codegen/config.toml` `[cores.default].meta`): whether this
  call needs `KC-API-*` HMAC signing. Hand-written to match that declared JSON Schema --
  never code-generated (design §2/§6, the same precedent this repo already uses for a
  spec-declared timestamp `format`; S27)."""

  signed: NotRequired[bool]
  """Whether this call needs `KC-API-*` HMAC signing (absent/`False` for every public endpoint)."""


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    content: bytes | None = None,
    headers: Mapping[str, str] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request, returning the unwrapped, optionally-validated result."""
    ...

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    content: bytes | None = None,
    headers: Mapping[str, str] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request, returning the unwrapped, optionally-validated result.

    Raises:
      AuthError: This transport was built with no credentials.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for KuCoin REST endpoint classes/mixins -- the resolved `default` core
  for every Classic product subtree (`codegen/config.toml`)."""

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
    `request_type`'s validator (ADR 0020/S28) into a plain, wire-ready dict, fill any
    `{placeholder}` segment of `path` from that dict (design §7 -- a path parameter is
    derived from the template string itself, never a spec-declared role marker), pull
    `x-tenant` out to a real header if present, route the remainder to the query string
    for a GET/DELETE or the JSON body for a POST/PUT (KuCoin's own, fully consistent
    convention -- confirmed against every currently-declared endpoint: every GET/DELETE
    is bare `parameters[]`, every POST/PUT declares a real body), and dispatch to
    `self.client.request`/`.authed_request` per `meta['signed']`.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire URL path, possibly `{placeholder}`-templated.
      meta: This call's own quirks -- whether it needs `KC-API-*` HMAC signing.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    values = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    path, values = substitute_template(path, values)
    headers: dict[str, str] | None = None
    if values is not None and HEADER_FIELD in values:
      values = dict(values)
      headers = {HEADER_FIELD: values.pop(HEADER_FIELD)}
      if not values:
        values = None
    is_query = method.upper() in ('GET', 'DELETE')
    params = values if is_query else None
    body = values if not is_query else None
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = self.client.authed_request if meta.get('signed', False) else self.client.request
    return await call(
      method, path, params=params, json=body, headers=headers,
      validator=response_validator, validate=validate,
    )
