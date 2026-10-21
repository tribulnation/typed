"""Base endpoint classes for every HTTP surface (`info`, `exchange`, `user`, `solana`, `public`,
`coingecko`): one `request()` call per endpoint method.

All six share one host, one error model and one signer, so they share one transport; they
differ in route and in whether a call is signed, which is per-endpoint `meta`.

- `RpcEndpoint` (`public`, `coingecko`): `path` is the real URL path.
- `ActionEndpoint` (`info`, `exchange`, `user`, `solana`): every call posts to one fixed
  route, selected by a `type` field in the body. `path` is that `type` value (`l2Book`,
  `order`), and the body is `{"type": path, **fields}`, as on Hyperliquid. Each surface's
  subclass knows its own route.
"""

from typing_extensions import (
  Any,
  ClassVar,
  Literal,
  NotRequired,
  Protocol,
  Self,
  TypedDict,
  TypeVar,
)
from dataclasses import dataclass
from types import UnionType

from typed_core.validation import validator

from .wire import dump_request

T = TypeVar('T')

Method = Literal['GET', 'POST']
"""HTTP verbs the API uses."""

Auth = Literal['none', 'signed', 'master']
"""Whether a call is sent unsigned, signed by the wallet (master or agent), or signed by the
master key only (agent management, withdrawals).
"""


class Meta(TypedDict):
  """Per-endpoint quirks of an HTTP call."""

  auth: NotRequired[Literal['signed', 'master']]
  """Signature requirement; absent means the call is sent unsigned. `signed` wraps the
  request into the signed envelope (master or agent key), `master` additionally refuses an
  agent key.
  """
  testnet_only: NotRequired[Literal[True]]
  """The action exists on testnet only (`faucetClaim`); refused locally on mainnet."""


class RpcClient(Protocol):
  """Structural interface the HTTP transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    method: Method,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    auth: Auth = 'none',
    testnet_only: bool = False,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request, unwrap the envelope and map errors, then validate.

    Args:
      method: HTTP verb.
      path: URL path.
      params: Query parameters (`GET`).
      body: JSON body (`POST`); the action itself when the call is signed.
      auth: Signature requirement.
      testnet_only: Refuse the call locally on mainnet.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    ...

  async def __aenter__(self) -> Self:
    """Take ownership of the connection pool (connecting lazily, on the first request)."""
    ...

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection pool."""
    ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for HTTP endpoints addressed by URL path (`public`, `coingecko`)."""

  client: RpcClient
  """The HTTP transport, shared by every HTTP surface."""

  async def __aenter__(self) -> Self:
    """Return this surface; the transport opens lazily, on first use.

    Opens and closes nothing: the transport is shared with sibling surfaces, and only the
    root client closes it.
    """
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client closes the shared transport."""

  async def request(
    self,
    request: Any = None,
    *,
    method: Method,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one HTTP call: `GET` values go in the query string, `POST` ones in the JSON
    body, wrapped into the signed envelope when `meta['auth']` says so.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: Wire HTTP verb.
      path: Wire URL path (`/version`, `/public/leaderboard`, ...).
      meta: This call's quirks: its signature requirement.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    return await self.send(
      method,
      path,
      dump_request(request, request_type),
      meta=meta,
      validate=validate,
      response_type=response_type,
    )

  async def send(
    self,
    method: Method,
    path: str,
    values: dict[str, Any],
    *,
    meta: Meta,
    validate: bool | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Send already-dumped `values` to the URL `path`: the query string for `GET`, the JSON
    body for `POST`.
    """
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return await self.client.request(
      method,
      path,
      params=values if method == 'GET' else None,
      body=values if method == 'POST' else None,
      auth=meta.get('auth', 'none'),
      testnet_only=meta.get('testnet_only', False),
      validator=response_validator,
      validate=validate,
    )


@dataclass(kw_only=True, frozen=True)
class ActionEndpoint(RpcEndpoint):
  """Base class for the `type`-dispatched routes: every call posts `{"type": path, ...}` to
  the surface's one `route`.
  """

  route: ClassVar[str]
  """The URL path every call of this surface posts to."""

  async def request(
    self,
    request: Any = None,
    *,
    method: Method,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one call: `{"type": path, **fields}` is posted to `route`, signed when
    `meta['auth']` says so.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: Wire HTTP verb (always `POST`).
      path: The wire `type` value (`l2Book`, `order`, `getUser`, ...).
      meta: This call's quirks: its signature requirement.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    values = {'type': path, **dump_request(request, request_type)}
    return await self.send(
      method,
      self.route,
      values,
      meta=meta,
      validate=validate,
      response_type=response_type,
    )


@dataclass(kw_only=True, frozen=True)
class InfoEndpoint(ActionEndpoint):
  """Base class for `info` endpoints: unsigned reads over `POST /info`."""

  route: ClassVar[str] = '/info'


@dataclass(kw_only=True, frozen=True)
class ExchangeEndpoint(ActionEndpoint):
  """Base class for `exchange` endpoints: signed actions over `POST /exchange`."""

  route: ClassVar[str] = '/exchange'


@dataclass(kw_only=True, frozen=True)
class UserEndpoint(ActionEndpoint):
  """Base class for `user` endpoints: signed or unsigned calls over `POST /user`."""

  route: ClassVar[str] = '/user'


@dataclass(kw_only=True, frozen=True)
class SolanaEndpoint(ActionEndpoint):
  """Base class for `solana` endpoints: signed calls over `POST /solana`."""

  route: ClassVar[str] = '/solana'
