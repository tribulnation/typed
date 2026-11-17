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

from ..signing import SignKind
from .wire import dump_request, fill_path

T = TypeVar('T')

Method = Literal['GET', 'POST', 'PUT', 'DELETE']
"""HTTP verbs the REST API uses."""


class Meta(TypedDict):
  """Per-endpoint quirks of a REST call. Every key is optional: `{}` is a public call whose
  fields go in the query string (`GET`) or a JSON body (`POST`/`PUT`).
  """

  auth: NotRequired[Literal['jwt']]
  """`jwt` when the call needs `Authorization: Bearer` (the "my ..." reads: fees, points,
  affiliate, allowance, sessions); absent when public. The client logs in lazily."""
  sign: NotRequired[SignKind]
  """What the body authorizes, so the core can sign it (`core.signing`): a signer permit
  (`place_order`, `cancel_order`, ...), an account setup action (`register_signer`,
  `revoke_signer`, `approve_single`) or a `login`. The caller passes the action's own fields
  only; signatures, nonces and the `account`/`signer` identities are filled in."""


class RpcClient(Protocol):
  """Structural interface the REST transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    method: Method,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Mapping[str, Any] | None = None,
    auth: Literal['jwt'] | None = None,
    sign: SignKind | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request, unwrap the envelope and map errors, then validate.

    Args:
      method: HTTP verb.
      path: URL path, placeholders already filled.
      params: Query parameters.
      json: JSON body fields.
      auth: Authenticate with a JWT.
      sign: Sign `json` for this action first.
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
    query string (`GET`) or the JSON body, and authenticate or sign per `meta`.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: HTTP verb.
      path: URL path, possibly with `{placeholders}` filled from `request`.
      meta: This call's quirks: JWT authentication, or what to sign.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    path = fill_path(path, values)
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    in_query = method == 'GET'
    return await self.client.request(
      method,
      path,
      params=values if in_query else None,
      json=None if in_query else values,
      auth=meta.get('auth'),
      sign=meta.get('sign'),
      validator=response_validator,
      validate=validate,
    )
