"""Base endpoint class for Deribit's JSON-RPC method surface -- the resolved `rpc` core
(`codegen/config.toml`, design §5).

Deribit is JSON-RPC (`method` + `params`), not REST-shaped (verb + path) -- `RpcClient`
takes just those two, unlike a REST venue's `request(method, path, ...)`. Deribit is also
the fleet's only genuine dual-transport surface (design §2's "Transport" subsection):
167 of its 178 rpc endpoints are reachable identically over HTTP or WebSocket, and the
generated call threads a per-call `transport` argument straight through to `request()`
below rather than choosing a transport once at construction (compare
`typed_hyperliquid.exchange.core.ExchangeCore`, the direct precedent this mirrors).
"""

from typing_extensions import (
  Any,
  Literal,
  Mapping,
  NotRequired,
  Protocol,
  Self,
  TypedDict,
  TypeVar,
  cast,
)
from types import UnionType
from dataclasses import dataclass
import json

from typed_core.validation import validator

T = TypeVar('T')


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`: one JSON-RPC
  method call, unauthenticated or authenticated."""

  async def request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T: ...

  async def authed_request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


class Meta(TypedDict):
  """`rpc`'s own `meta` shape (`codegen/config.toml` `[cores.rpc].meta`): whether this call is
  public. Hand-written to match that declared JSON Schema -- never code-generated
  (design §2/§6, the same precedent this repo already uses for a spec-declared
  timestamp `format`; S27)."""

  public: NotRequired[bool]
  """`True` for a call that needs no credentials. Absent (or `False`) for the majority
  of the surface, which needs the client's standard credential -- `Deribit`'s Bearer
  token (`http_auth='token'`) or per-request HMAC signature (`http_auth='hmac'`) over
  HTTP, or a fetched `access_token` over WebSocket."""


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for Deribit JSON-RPC endpoint groups -- the resolved `rpc` core."""

  client: RpcClient
  """The default transport (`transport='http'` for a dual-transport endpoint; the only
  transport for an HTTP-reachable one)."""
  ws_client: RpcClient | None = None
  """The alternate transport a per-call `transport='ws'` selects. Also the *only*
  transport for one of Deribit's 11 WS-only rpc commands (`session.set_heartbeat`,
  `trading.mass_quote`, ...) -- `request`'s own `transport` default (`'ws'`) is what
  makes those correct with no caller-facing parameter at all: a WS-only endpoint's
  generated call never passes `transport=` (design §2, "a length-1 `transports`...
  produces no parameter at all"), so it always falls through to this default, and every
  real single-transport rpc endpoint in this client's spec is WS-only -- there is no
  single-transport HTTP-only case to conflict with it."""

  @classmethod
  def new(cls, client: RpcClient, *, ws_client: RpcClient | None = None) -> Self:
    """Build one rpc section forwarding the root's already-built transports (design
    §5a) -- not meant to be called directly; each generated `@cached_property` on
    `Deribit` calls this, forwarding `ClientBase`'s own same-named `ws_client` field.
    """
    return cls(client=client, ws_client=ws_client)

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    if self.ws_client is not None:
      await self.ws_client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)
    if self.ws_client is not None:
      await self.ws_client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str | None = None,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | object | None = None,
    response_type: type[T] | UnionType | object | None = None,
    transport: Literal['http', 'ws'] = 'ws',
  ) -> T:
    """Perform one JSON-RPC call (design §2's single verb): serialize `request` through
    `request_type`'s validator (ADR 0020/S28) into a plain `params` dict, send it over
    the requested transport -- signed (`authed_request`) unless `meta['public']` -- and
    validate the reply's own already-unwrapped result through `response_type`'s
    validator. Envelope unwrapping happens inside the transport itself
    (`core/transport/http.py`/`core/transport/ws.py`'s own `result()`/`call()`), so
    nothing here has to know about `envelope.payload`/`correlate`.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, a discriminated-
        union variant for `trading.buy`/`sell`/`close_position`, or `None` for a
        parameterless method).
      method: Unused -- every Deribit call is `POST`; kept only so this signature
        matches every other resolved core's `request()`.
      path: The JSON-RPC method name, e.g. `public/get_time`.
      meta: `endpoint.meta`, checked against `codegen/config.toml`'s `[cores.rpc].meta` schema
        at spec-test time (design §2/§6) -- `public` picks `request` vs `authed_request`.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply. Typed
        `type[T] | UnionType | object | None` rather than the narrower `type[T] |
        UnionType | None` other clients' cores use -- confirmed live: pyright accepts a
        multi-value `Literal['a', 'b']` alias fine (it synthesizes as `UnionType`), but
        genuinely rejects a *single*-value one (`Literal['ok']`, common on Deribit's
        many bare `"ok"`-acknowledgement responses) against `type[T]`, synthesizing it
        as `type[Literal['ok']]` and refusing to bind `T` from it -- confirmed a pyright
        limitation, not a codegen defect: even a bare, non-generic `type` parameter
        rejects it identically. The `object` fallback arm only ever matches that one
        pyright-unsolvable shape; `type[T]` still wins (and `T` still narrows correctly)
        for every ordinary class response.
      transport: Which connection carries this call -- `self.client` (`'http'`) or
        `self.ws_client` (`'ws'`). Deribit's own reply is byte-identical either way for
        every dual-transport method.

    Raises:
      ValueError: `transport='ws'` was requested, but this instance has no WebSocket
        transport configured.
    """
    if transport == 'ws':
      if self.ws_client is None:
        raise ValueError('No WebSocket transport is configured for this client.')
      client = self.ws_client
    else:
      client = self.client
    params = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = client.request if meta.get('public', False) else client.authed_request
    return await call(
      path, params=params, validator=response_validator, validate=validate
    )
