"""Base endpoint class for the Trading API's REST operations: one `request()` call per
endpoint method, whose `meta` says how the call authenticates."""

from typing_extensions import (
  Any,
  Literal,
  Mapping,
  NotRequired,
  Protocol,
  Self,
  TypedDict,
  TypeVar,
)
from dataclasses import dataclass
from types import UnionType

from typed_core.validation import validator

from ..exc import LogicError
from .wire import dump_request, fill_path

T = TypeVar('T')

Method = Literal['GET', 'POST', 'PATCH', 'DELETE']
"""HTTP verbs the Trading API uses."""

AuthMode = Literal['read', 'trade']
"""How a private call authenticates:

- `read`: a private read. A read-only API key when the client has one, else the agent
  signature.
- `trade`: a write. Always the agent signature.
"""


class Meta(TypedDict):
  """Per-endpoint facts of a Trading API call. `{}` is a public call under the chain root."""

  auth: NotRequired[AuthMode]
  """How the call authenticates; absent when it is public (agent registration and API-key
  issuance are public too: the master wallet's signature travels in their body)."""
  operation: NotRequired[str]
  """The OpenAPI `operationId` (`getAccount`, `createOrder`, ...), the EIP-712 primary
  type of the agent signature. Required with `auth`."""
  root: NotRequired[Literal['host']]
  """`host` for the two operations outside the chain root (`/health`, `/ready`): their
  `path` is relative to the API host instead."""
  unwrap: NotRequired[Literal['data']]
  """`data` for a list endpoint answering `{"data": [...]}`: return the list. Absent on
  single resources (bare objects) and on cursor pages (`{data, nextCursor}`, kept whole
  for the walk)."""


class TradingClient(Protocol):
  """Structural interface the Trading API's HTTP transport implements."""

  async def request(
    self,
    method: Method,
    path: str,
    *,
    query: Mapping[str, Any] | None = None,
    body: Mapping[str, Any] | None = None,
    auth: AuthMode | None = None,
    operation: str | None = None,
    root: Literal['chain', 'host'] = 'chain',
    unwrap: str | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request, authenticate it per `auth`, map errors, unwrap and validate.

    Args:
      method: HTTP verb.
      path: Path relative to `root`, placeholders already filled.
      query: Query parameters.
      body: JSON body fields; `None` sends no body.
      auth: How the call authenticates; `None` when public.
      operation: The `operationId` the agent signature names; required with `auth`.
      root: Resolve `path` against the chain root (`/v1/{chain}`) or the API host.
      unwrap: Key whose value the call returns instead of the whole body.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class TradingEndpoint:
  """Base class for Trading API REST endpoints."""

  client: TradingClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

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
    """Perform one Trading API call: fill `path`'s placeholders from `request`, put the
    remaining fields in the query string (`GET`) or the JSON body (otherwise), and
    authenticate per `meta`.

    A `DELETE` sends a body only when fields remain (`revokeAgent` carries the master
    signature; `cancelOrder` has none); `POST` and `PATCH` always send one.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: HTTP verb.
      path: Path relative to the chain root (or the host, per `meta`), with
        `{placeholders}` filled from `request`.
      meta: This call's authentication, root and envelope.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.

    Raises:
      LogicError: `meta` declares `auth` without its `operation`.
    """
    values = dump_request(request, request_type)
    path = fill_path(path, values)
    auth = meta.get('auth')
    operation = meta.get('operation')
    if auth is not None and operation is None:
      raise LogicError(
        f'{method} {path}: an authenticated endpoint must declare its `operation`.'
      )
    if method == 'GET':
      query, body = values, None
    elif method == 'DELETE':
      query, body = None, (values or None)
    else:
      query, body = None, values
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return await self.client.request(
      method,
      path,
      query=query,
      body=body,
      auth=auth,
      operation=operation,
      root=meta.get('root', 'chain'),
      unwrap=meta.get('unwrap'),
      validator=response_validator,
      validate=validate,
    )
