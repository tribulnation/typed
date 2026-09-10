"""`RpcEndpoint`: the one resolved core every generated Etherscan endpoint subclasses
(design §2's single `request()` verb).

Etherscan's whole surface is one plain REST host multiplexed by fixed `module`/`action`
query constants (`/v2/api`), plus one endpoint outside that dispatch (`/v2/chainlist`,
`usage.chain_list`) -- there is no JSON-RPC framing and no WebSocket transport, so this
is the client's only resolved core (design §5's degenerate single-core case).

Wire placement is a fixed, per-field convention this core owns (design §2), not spec
data: `module`/`action`/`chainid` -- Etherscan's own dispatch constants, present on
nearly every endpoint's `request` schema -- always travel on the query string, on every
verb; every other field follows the declared HTTP verb, query string for `GET`, an
`application/x-www-form-urlencoded` body for anything else (`contracts.verify_*`'s own
submission fields). This is the real, live wire fact the client's pre-migration core
already encoded per-endpoint (`EtherscanGenerator._form_body_arg`) -- collapsed here into
one fixed rule `core` applies uniformly, per design §7's own "location markers are
eliminated, not redeclared."
"""

from typing_extensions import Any, NotRequired, Self, TypedDict, TypeVar, cast
from types import UnionType
from dataclasses import dataclass
import json

import httpx

from typed_core.exceptions import AuthError
from typed_core.validation import validator

from .base import EtherscanTransport
from .envelope import unwrap

T = TypeVar('T')

DISPATCH_KEYS = frozenset({'module', 'action', 'chainid'})
"""Etherscan's own fixed `/v2/api` dispatch constants -- always sent on the query
string, regardless of HTTP verb, never folded into a POST's form body."""


class Meta(TypedDict):
  """`meta`'s shape for this core (`codegen/config.toml`'s `[cores.http]`) -- hand-written to
  match the declared JSON Schema exactly, never code-generated (design §2/§6)."""

  credentials: NotRequired[bool]
  """Whether this endpoint requires the API key attached as the `apikey` query
  parameter -- absent (or `False`) only on `usage.chain_list`, the one endpoint
  reachable with no API key at all; `True` on every other endpoint."""


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for every generated Etherscan endpoint, sharing one transport."""

  client: EtherscanTransport

  async def __aenter__(self) -> Self:
    await self.client.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.http.__aexit__(exc_type, exc_value, traceback)

  async def _send(
    self, method: str, path: str, *, params: dict[str, Any] | None, data: dict[str, Any] | None,
  ) -> httpx.Response:
    url = self.client.base_url + path
    if self.client.rate_limit is None:
      return await self.client.http.request(method, url, params=params, data=data)
    async with self.client.rate_limit:
      return await self.client.http.request(method, url, params=params, data=data)

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
    meta: Meta = {},
  ) -> T:
    """Perform one call: serialize `request` through `request_type`'s validator
    (ADR 0020/S28), split it into query vs form-body per `DISPATCH_KEYS`/`method`, attach
    the API key when `meta['credentials']` is set, and validate the reply through
    `response_type`'s validator.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire path (`/v2/api` or `/v2/chainlist`).
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
      meta: A plain dict literal matching this class's own hand-written `Meta` (design
        §2/§6) -- `credentials` attaches the API key as the `apikey` query parameter,
        raising if this client was built with no key.

    Raises:
      AuthError: `meta['credentials']` is set and this client was built with no API key
        (`public=True` upstream).
    """
    # `validator(...).dump(...)` returns JSON *bytes* -- round-tripping through
    # `json.loads` gets a wire-ready dict back, with every declared format's
    # `PlainSerializer` (S27) already applied, so the epoch-seconds/decimal-string/etc.
    # conversions happen exactly once regardless of which channel a field ends up on.
    values = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else {}
    )
    query = {key: value for key, value in values.items() if key in DISPATCH_KEYS or method == 'GET'}
    body = {key: value for key, value in values.items() if key not in DISPATCH_KEYS and method != 'GET'}
    if meta.get('credentials'):
      if self.client.api_key is None:
        raise AuthError('No credentials: this client was built with `public=True`.')
      query = {'apikey': self.client.api_key, **query}
    response = await self._send(method, path, params=query or None, data=body or None)
    payload = unwrap(response)
    if response_type is None:
      return None  # type: ignore[return-value]
    if not self.client.should_validate(validate):
      return payload  # type: ignore[return-value]
    return validator(cast(type, response_type)).python(payload)
