"""Base endpoint class for bit2me's `http` surface (Crypto API v1/v2/v3, Embed API,
Trading Spot REST -- one shared host/auth/envelope, `spec/core.md`'s Surfaces section):
design §2's single `request()` verb, deciding public-vs-signed purely from `meta`'s own
dict literal, matching `codegen/config.toml`'s `[cores.http].meta` schema.
"""

from typing_extensions import Any, NotRequired, Protocol, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.validation import validator

T = TypeVar('T')


class Meta(TypedDict):
  """`http`'s own `meta` shape (`codegen/config.toml` `[cores.http].meta`), hand-written to
  match that declared JSON Schema -- never code-generated (design §2/§6, the same
  precedent this repo already uses for a spec-declared timestamp `format`; S27). Kept
  to the minimum set of literal keys that discriminates real distinct behavior
  (`docs/spec/authoring.md` rule 9): `{}` (absent/`False` for both) is the standard
  signed case, most endpoints; `public` opts out of signing; `two_factor` signs exactly
  like the standard case but additionally requires an already-enrolled account's 2FA
  header (`x-totp`/`x-totp-type`) -- a real, documented per-call requirement
  `spec/core.md`'s own prior pass explicitly left out of the core (a per-endpoint
  header, not a transport-level concern). Named `two_factor` rather than the venue's own
  `totp` wire name to avoid colliding with the two `.../two_factor/enable_finish`
  endpoints' own genuine `totp` request-body field (design §2's collision check, the
  same shape S8 flags for a wire parameter literally named `validate`) --
  `two_factor` still just signs the request here, matching that decision and the old
  backend's own actual behavior (`bool(endpoint.meta)` never distinguished the two
  either); the 2FA code itself never reached a header on any bit2me endpoint before this
  migration, and doesn't start doing so now."""

  public: NotRequired[bool]
  """Whether this call is unsigned (absent/`False` for every signed endpoint)."""
  two_factor: NotRequired[bool]
  """Whether this call additionally requires an already-enrolled account's 2FA header
  -- not yet threaded to the wire (see class docstring)."""


class RpcClient(Protocol):
  """What an endpoint needs from its transport: request/reply, public or authenticated."""

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
  ) -> T: ...
  async def __aenter__(self) -> Self: ...
  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base for every generated `http`-surface endpoint method -- the resolved `core` for
  the whole `v1`/`v2`/`v3` subtree (`codegen/config.toml`)."""

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
    """Perform one `http` call (design §2's single verb): serialize `request` through
    `request_type`'s validator (ADR 0020/S28) into a plain, wire-ready dict, route it as
    the query string for a GET or the JSON body for a write, sign it when `meta` calls
    for it, and validate the reply through `response_type`'s validator.

    A templated path segment (e.g. `{orderId}`) is substituted from `request`'s own
    matching key before the remaining fields are sent as query/body.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire path template, e.g. `/v1/loan/orders/{orderId}`.
      meta: This call's own quirks -- see `Meta`.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    values: dict[str, Any] = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else {}
    )
    resolved_path = path
    for key in list(values):
      placeholder = '{' + key + '}'
      if placeholder in resolved_path:
        resolved_path = resolved_path.replace(placeholder, str(values.pop(key)))
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    as_query = method.upper() in ('GET', 'DELETE')
    query = values or None if as_query else None
    body = values or None if not as_query else None
    call = self.client.authed_request if not meta.get('public') else self.client.request
    return await call(
      method, resolved_path, params=query, json=body,
      validator=response_validator, validate=validate,
    )
