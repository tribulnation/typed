"""Base endpoint class for Kraken Spot's HTTP endpoints: design §2's single `request()`
verb, deciding public-vs-signed and form-vs-JSON body purely from `meta['signed']` --
every generated call's own `meta` dict literal, matching `codegen/config.toml`'s
`[cores.spot].meta` schema -- and from `path`. `core` decides everything about wire
mechanics (design §2), including which of the venue's two body encodings a given private
endpoint takes.
"""

from typing_extensions import Any, NotRequired, Protocol, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.validation import validator

T = TypeVar('T')


class Meta(TypedDict):
  """`spot`'s own `meta` shape (`codegen/config.toml` `[cores.spot].meta`): whether this call
  needs HMAC-SHA512 signing. Hand-written to match that declared JSON Schema -- never
  code-generated (design §2/§6, the same precedent this repo already uses for a
  spec-declared timestamp `format`; S27)."""

  signed: NotRequired[bool]
  """Whether this call needs HMAC-SHA512 signing (absent/`False` for every public endpoint)."""


JSON_BODY_PATHS = {
  '/0/private/AddOrderBatch',
  '/0/private/CancelOrderBatch',
}
"""Private Spot endpoints Kraken rejects a form-urlencoded body on -- confirmed live
(`spec/status.md`). A fixed per-path table: the wire-shape dispatch a generated call
can't see (design §7 already sanctions this -- alchemy's own `core.rpc.ChainRpc`
positional-JSON-RPC dispatch is the precedent), not spec data."""


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    path: str,
    params: dict[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned GET request to a public endpoint."""
    ...

  async def authed_request(
    self,
    path: str,
    data: dict[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send a form-urlencoded POST request to a private endpoint.

    Raises:
      AuthError: This transport was built with no credentials (`public=True` upstream).
    """
    ...

  async def authed_json_request(
    self,
    path: str,
    data: dict[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send a POST request with a JSON body, for the two endpoints Kraken
    rejects a form-urlencoded body on (`JSON_BODY_PATHS`).

    Raises:
      AuthError: This transport was built with no credentials (`public=True` upstream).
    """
    ...

  async def authed_raw_request(
    self,
    path: str,
    data: dict[str, Any] | None = None,
    *,
    validate: bool | None = None,
  ) -> bytes:
    """Sign and send a POST request to a private endpoint whose response is not the
    standard `{error, result}` JSON envelope (`retrieve_export`'s binary export file).

    Raises:
      AuthError: This transport was built with no credentials (`public=True` upstream).
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for Kraken Spot HTTP endpoints -- the resolved `core` for the whole
  `spot/` subtree (`codegen/config.toml`)."""

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
    """Perform one Spot REST call (design §2's single verb): serialize `request` through
    `request_type`'s validator (ADR 0020/S28) into a plain, wire-ready dict, route it to
    the query string for an unsigned public call or the body of a signed private one
    (form-urlencoded, except `JSON_BODY_PATHS`), and validate the reply through
    `response_type`'s validator.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb -- every real Spot GET is public and every real Spot POST is
        private, so `meta['signed']` alone already decides which transport method to
        call; kept so every generated call can pass it uniformly (design §2), not read
        here.
      path: Wire path, e.g. `/0/private/Balance`.
      meta: This call's own quirks -- whether it needs HMAC-SHA512 signing (`endpoint.
        meta`'s own `signed` key, absent/`False` for every public endpoint).
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    # `validator(...).dump(...)` returns JSON *bytes* (`typed_core.validation.validator.
    # dump`'s own signature) -- round-tripping through `json.loads` gets a plain dict
    # back with every declared format's `PlainSerializer` (S27) already applied, the
    # right shape for both an unsigned GET's query string and a signed POST's form/JSON
    # body.
    values = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    if not meta.get('signed', False):
      return await self.client.request(
        path, values, validator=response_validator, validate=validate
      )
    if path in JSON_BODY_PATHS:
      return await self.client.authed_json_request(
        path, values, validator=response_validator, validate=validate
      )
    return await self.client.authed_request(
      path, values, validator=response_validator, validate=validate
    )
