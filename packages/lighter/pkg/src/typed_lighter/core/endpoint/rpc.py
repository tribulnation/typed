"""Base endpoint class for the main REST API (`client.api`): one `request()` call per endpoint method."""

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

from .wire import dump_request, fill_path

T = TypeVar('T')

Method = Literal['GET', 'POST']
"""HTTP verbs the main REST API uses."""

Auth = Literal['none', 'optional', 'token', 'write']
"""What a call needs: nothing, a token if one is configured, any token, or a write-capable
(derived) token."""


class Meta(TypedDict):
  """Per-endpoint quirks of a main REST API call."""

  auth: NotRequired[Literal['optional', 'token', 'write']]
  """Token requirement; absent means the call is public. `optional` attaches a token when
  one is configured (public-pool trades vs an account's own), `token` needs one (derived or
  `ro:`), `write` needs a derived one (token-gated writes: `tokens/create`, `referral/*`, ...)."""


class RpcClient(Protocol):
  """Structural interface the REST transport implements to back an `RpcEndpoint`."""

  async def request(
    self,
    method: Method,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    form: Mapping[str, Any] | None = None,
    auth: Auth = 'none',
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request, unwrap the envelope and map errors, then validate.

    Args:
      method: HTTP verb.
      path: URL path, placeholders already filled.
      params: Query parameters.
      form: Form-encoded body fields.
      auth: Token requirement.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    ...


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for main REST API endpoints."""

  client: RpcClient
  """The REST transport."""

  async def __aenter__(self) -> Self:
    """Return this surface; the REST transport opens lazily, on first use.

    Entering or leaving it with `async with` opens and closes nothing: the transport is shared
    with sibling surfaces, and only the root client (`core.client.ClientBase`) closes it.
    """
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client closes the REST transport, which sibling surfaces
    may still be using."""

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
    """Perform one REST call: `GET` parameters go in the query string, `POST` ones in a
    form body, and a token is attached per `meta['auth']`.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: Wire HTTP verb.
      path: Wire URL path, possibly with `{placeholders}` filled from `request`.
      meta: This call's quirks: its token requirement.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    path = fill_path(path, values)
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    auth: Auth = meta.get('auth', 'none')
    if method == 'GET':
      return await self.client.request(
        method,
        path,
        params=values,
        auth=auth,
        validator=response_validator,
        validate=validate,
      )
    return await self.client.request(
      method,
      path,
      form=values,
      auth=auth,
      validator=response_validator,
      validate=validate,
    )
