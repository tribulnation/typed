"""Base endpoint class for the REST API: one `request()` call per endpoint method."""

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

from ..envelope import EnvelopeMode
from .wire import dump_request, fill_path

T = TypeVar('T')

Method = Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
"""HTTP verbs the REST API uses."""

SignKind = Literal['order', 'transfer', 'withdrawal']
"""Which settlement a signed call carries."""


class Meta(TypedDict):
  """Per-endpoint quirks of a REST call. Every key is optional; `{}` is a public call whose
  fields go in the query string (`GET`/`DELETE`) or a JSON body (`POST`/`PUT`/`PATCH`)."""

  auth: NotRequired[Literal['api_key']]
  """`api_key` when the call needs the `X-Api-Key` header; absent when public."""
  sign: NotRequired[SignKind]
  """The Stark settlement the core builds and attaches before sending (implies `auth`):
  `order` (and each TP/SL leg), `transfer` or `withdrawal`."""
  envelope: NotRequired[Literal['page', 'frame']]
  """`page` for a paginated call: return `{data, pagination}` instead of bare `data`, so
  the walk can read `pagination.cursor`. `frame` for a call whose success carries no `data`
  (`POST /user/bridge/quote`): return the whole `{status}` frame."""
  params: NotRequired[Literal['query']]
  """`query` when a `POST`'s fields go in the query string rather than a JSON body
  (`POST /user/bridge/quote?id=`, `POST /user/deadmanswitch?countdownTime=`)."""


class RpcClient(Protocol):
  """Structural interface the REST transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    method: Method,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Mapping[str, Any] | None = None,
    auth: bool = False,
    sign: SignKind | None = None,
    envelope: EnvelopeMode = 'data',
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request, unwrap the envelope and map errors, then validate.

    Args:
      method: HTTP verb.
      path: URL path below the `/api/v1` base, placeholders already filled.
      params: Query parameters.
      json: JSON body fields.
      auth: Send the API key.
      sign: Build and attach this Stark settlement to `json` first.
      envelope: What the successful envelope unwraps to (`core.envelope.EnvelopeMode`).
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for REST endpoints."""

  client: RpcClient
  """The REST transport."""

  async def __aenter__(self) -> Self:
    """Return this surface; the REST transport opens lazily, on first use.

    Entering or leaving it opens and closes nothing: the transport is shared with sibling
    surfaces, and only the root client (`core.client.ClientBase`) closes it.
    """
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client closes the shared REST transport."""

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
    """Perform one REST call: fill `path`'s placeholders, put the remaining fields in the
    query string or the JSON body, and authenticate and sign per `meta`.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: HTTP verb.
      path: URL path, possibly with `{placeholders}` filled from `request`.
      meta: This call's quirks: authentication, signing, pagination envelope, placement.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    path = fill_path(path, values)
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    sign = meta.get('sign')
    in_query = method in ('GET', 'DELETE') or meta.get('params') == 'query'
    return await self.client.request(
      method,
      path,
      params=values if in_query else None,
      json=None if in_query else values,
      auth=sign is not None or meta.get('auth') == 'api_key',
      sign=sign,
      envelope=meta.get('envelope', 'data'),
      validator=response_validator,
      validate=validate,
    )
