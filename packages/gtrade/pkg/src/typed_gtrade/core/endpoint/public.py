"""Base endpoint class for the public, unauthenticated REST backends: the per-chain trading
backend, Backend Global and pricing. They share one envelope family and no credentials;
only the host differs."""

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
"""HTTP verbs the public reads use (Backend Global's batch reads are `POST`s)."""


class Meta(TypedDict):
  """Per-endpoint facts of a public backend call. `{}` returns the bare body."""

  unwrap: NotRequired[Literal['result']]
  """`result` for Backend Global's referral reads, which answer `{"result": ...}`:
  return the inner value."""


class PublicClient(Protocol):
  """Structural interface the public backends' HTTP transport implements."""

  async def request(
    self,
    method: Method,
    path: str,
    *,
    query: Mapping[str, Any] | None = None,
    body: Mapping[str, Any] | None = None,
    unwrap: str | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request, map errors, unwrap and validate.

    Args:
      method: HTTP verb.
      path: Path relative to the host, placeholders already filled.
      query: Query parameters.
      body: JSON body fields; `None` sends no body.
      unwrap: Key whose value the call returns instead of the whole body.
      validator: Response validator.
      validate: Per-call override of response validation.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class PublicEndpoint:
  """Base class for public backend REST endpoints."""

  client: PublicClient

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
    """Perform one public call: fill `path`'s placeholders from `request` (a list value is
    comma-joined: `/trading-variables/{keys}`), and put the remaining fields in the query
    string (`GET`) or the JSON body (`POST`).

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: HTTP verb.
      path: Path relative to the host, with `{placeholders}` filled from `request`.
      meta: This call's envelope.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    path = fill_path(path, values)
    get = method == 'GET'
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return await self.client.request(
      method,
      path,
      query=values if get else None,
      body=None if get else values,
      unwrap=meta.get('unwrap'),
      validator=response_validator,
      validate=validate,
    )
