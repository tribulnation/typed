"""Base endpoint class for REST-shaped RPC endpoints: design §2's single `request()` verb,
deciding public/keyed/signed dispatch purely from `meta['signed']`/`meta['security']`, and
routing `lang` (Binance's only declared `in: 'header'` parameter) to a real HTTP header
rather than a query/form field.
"""

from typing_extensions import Any, Mapping, NotRequired, Protocol, Self, TypedDict, TypeVar
from dataclasses import dataclass
from types import UnionType

from typed_core.validation import validator

from .wire import dump_request, wire_params

T = TypeVar('T')


class Meta(TypedDict):
  """`http_rpc`'s own `meta` shape (`codegen/config.toml` `[cores.http_rpc].meta`): Binance's
  documented security tier, and whether the call must be HMAC-signed. Hand-written to
  match that declared JSON Schema -- never code-generated (design §2/§6; S27's own
  precedent)."""

  security: NotRequired[str]
  """Binance's documented security-tier label -- `TRADE`, `USER_DATA`, `MARGIN`, `SIGNED`,
  `MARKET_DATA`, `USER_STREAM`, `NONE`, or `System`."""
  signed: NotRequired[bool]
  """Whether this call must be HMAC-signed (`timestamp`/`recvWindow`/`signature` added,
  alongside the `X-MBX-APIKEY` header)."""


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`. No `json:`
  parameter: Binance never sends JSON bodies, only form-encoded `params` (see
  `spec/core.md`'s Authentication section)."""

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def keyed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for REST-shaped RPC endpoints. Every Binance REST surface (Spot, USD-M/
  COIN-M Futures, Options, Portfolio Margin) shares this shape -- only `client.base_url`
  and which methods a subclass adds differ."""

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
    `request_type`'s validator (ADR 0020/S28), route `lang` to a real header, and dispatch
    to `self.client.request`/`.keyed_request`/`.authed_request` per Binance's three real
    security tiers (`spec/core.md`'s Authentication section):

    - fully signed (`meta['signed']`, any `security` label) -> `authed_request`: adds
      `timestamp`/`recvWindow`/`signature`.
    - unsigned but still keyed (`MARKET_DATA`/`USER_STREAM`, and the one documented
      `USER_DATA` outlier that carries no signature at all,
      `spot.institutional_loan.risk_unit_ltv`) -> `keyed_request`: adds the API-key
      header, no signing.
    - genuinely public (`NONE`, absent, or the one-off `System` tag,
      `spot.wallet.others.system_status`) -> `request`: no credentials touched at all.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire URL path.
      meta: This call's own quirks -- security tier and signing requirement.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    params, lang = wire_params(values)
    headers = {'lang': lang} if lang is not None else None
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    if meta.get('signed', False):
      return await self.client.authed_request(
        method, path, params=params, headers=headers,
        validator=response_validator, validate=validate,
      )
    security = meta.get('security')
    if security in ('NONE', None, 'System'):
      return await self.client.request(
        method, path, params=params, headers=headers,
        validator=response_validator, validate=validate,
      )
    return await self.client.keyed_request(
      method, path, params=params, headers=headers,
      validator=response_validator, validate=validate,
    )
