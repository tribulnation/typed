"""Base endpoint class for RPC (REST request/reply) endpoints: design §2's single
`request()` verb, deciding public-vs-signed purely from `meta['signed']` -- every
generated call's own `meta` dict literal, matching `codegen/config.toml`'s `[cores.app_http]`/
`[cores.exchange_http]` meta schema -- and query-vs-body purely from `method` (every real
GET on this venue is public query params; every real POST/PUT/PATCH/DELETE is a JSON
body -- `core` decides everything about wire mechanics, design §2). A `{placeholder}` in
`path` is resolved from the matching `request` field, which is then excluded from the
remaining query/body payload -- design §7's "location markers are eliminated, not
redeclared."

Shared, auth-agnostic: both Coinbase App (`typed_coinbase.app.core.AppBase`) and Coinbase
Exchange (`typed_coinbase.exchange.core.ExchangeBase`) resolve their own HTTP subtrees to
this exact class -- only the pre-built `client` transport and the venue-specific `meta`
schema differ per subtree (design §5).
"""

from typing_extensions import Any, NotRequired, Protocol, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
from urllib.parse import quote
import json

from typed_core.validation import validator

T = TypeVar('T')


class Meta(TypedDict):
  """`app_http`'s and `exchange_http`'s shared `meta` shape (`codegen/config.toml`
  `[cores.app_http]`/`[cores.exchange_http]`): whether this call needs signing. Hand-
  written to match that declared JSON Schema -- never code-generated (design §2/§6, the
  same precedent this repo already uses for a spec-declared timestamp `format`; S27)."""

  signed: NotRequired[bool]
  """Whether this call needs a signed/authenticated request (absent/`False` for every
  public endpoint)."""


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
  ) -> T:
    """Send an unsigned request."""
    ...

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
  """Base class for every Coinbase HTTP endpoint -- the resolved `core` for both `app`'s
  and `exchange`'s own REST subtrees (design §5)."""

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
    `request_type`'s validator (ADR 0020/S28) into a plain, wire-ready dict, substitute
    any `{placeholder}` in `path` from a matching field, route the rest to the query
    string (`GET`) or a JSON body (every other verb), and validate the reply through
    `response_type`'s validator.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire path, e.g. `/v2/accounts/{account_id}/addresses` -- a `request` field
        whose name matches a `{placeholder}` here is a path parameter, substituted (URL-
        quoted) and excluded from the remaining query/body payload (design §7).
      meta: This call's own quirks -- whether it needs a signed request (`endpoint.
        meta`'s own `signed` key, absent/`False` for every public endpoint).
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    # `validator(...).dump(...)` returns JSON *bytes* -- round-tripping through
    # `json.loads` gets a plain dict back with every declared format's own
    # `PlainSerializer` (S27) already applied, the right shape for both a `GET`'s query
    # string and a signed body.
    values: dict[str, Any] = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else {}
    )
    resolved_path = path
    for key in list(values):
      placeholder = '{' + key + '}'
      if placeholder in resolved_path:
        resolved_path = resolved_path.replace(placeholder, quote(str(values.pop(key)), safe=''))
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = self.client.authed_request if meta.get('signed', False) else self.client.request
    if method.upper() == 'GET':
      return await call(
        method, resolved_path, params=values or None,
        validator=response_validator, validate=validate,
      )
    return await call(
      method, resolved_path, json=values or None,
      validator=response_validator, validate=validate,
    )
