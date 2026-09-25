"""Explorer API core (`client.explorer`): public, bare-JSON, its own host and error shape.

Successful responses are bare JSON (no envelope). Errors are `{"error": "<message>"}` with
an HTTP 4xx status, or a plain-text `404 page not found` for an unknown path. The explorer
has its own rate-limit pool (90 weight/min per IP).
"""

from typing_extensions import Any, Literal, Self, TypeVar
from dataclasses import dataclass, field
from types import UnionType

from typed_core.http import HttpClient
from typed_core.validation import validator
import httpx

from ..core.endpoint.wire import dump_request, fill_path, query_values
from ..core.exc import ApiError, BadRequest, LogicError, RateLimited

T = TypeVar('T')


@dataclass(kw_only=True)
class ExplorerClient:
  """HTTP client for one explorer deployment."""

  base_url: str | None
  """Explorer base URL; `None` when the configured network has no known explorer."""
  http: HttpClient = field(default_factory=HttpClient)
  """Connection pool."""
  validate: bool = True
  """Validate responses by default."""

  async def __aenter__(self) -> Self:
    """Take ownership of the connection pool without connecting (it opens lazily)."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection pool, if it was opened. Only the root client (`core.client.ClientBase`) calls this."""
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def result(self, response: httpx.Response) -> Any:
    """Return the JSON body, raising on an error status.

    Errors carry `(status, message, payload)`: the explorer has no business codes.

    Raises:
      RateLimited: Status 429.
      BadRequest: Any other 4xx.
      ApiError: 5xx.
    """
    try:
      payload: Any = response.json()
    except ValueError:
      payload = response.text[:500]
    if response.is_success:
      return payload
    message = str(payload.get('error', '') if isinstance(payload, dict) else payload)
    status = response.status_code
    if status == 429:
      raise RateLimited(status, message, payload)
    if 400 <= status < 500:
      raise BadRequest(status, message, payload)
    raise ApiError(status, message, payload)

  async def request(
    self,
    method: Literal['GET'],
    path: str,
    *,
    params: dict[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request and validate its JSON body.

    Args:
      method: HTTP verb (the explorer only serves reads).
      path: URL path.
      params: Query parameters.
      validator: Response validator.
      validate: Per-call override of response validation.

    Raises:
      LogicError: The configured network has no explorer.
    """
    if self.base_url is None:
      raise LogicError('This network has no known explorer API.')
    response = await self.http.request(
      method, self.base_url + path, params=query_values(params) if params else None
    )
    payload = self.result(response)
    should_validate = self.validate if validate is None else validate
    if validator is not None and should_validate:
      return validator.python(payload)
    return payload


@dataclass(kw_only=True, frozen=True)
class ExplorerEndpoint:
  """Base class for explorer endpoints."""

  client: ExplorerClient
  """The explorer transport."""

  async def __aenter__(self) -> Self:
    """Return this surface; the explorer transport opens lazily, on first use.

    Entering or leaving it with `async with` opens and closes nothing: the transport is shared
    with sibling surfaces, and only the root client (`core.client.ClientBase`) closes it.
    """
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client closes the explorer transport, which sibling surfaces
    may still be using."""

  async def request(
    self,
    request: Any = None,
    *,
    method: Literal['GET'],
    path: str,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one explorer call: path placeholders from `request`, the rest as query string.

    Args:
      request: The endpoint's `Request` value, or `None` for a parameterless call.
      method: Wire HTTP verb.
      path: Wire URL path, possibly with `{placeholders}`.
      validate: Per-call override of response validation.
      request_type: The endpoint's request type, used to serialize `request`.
      response_type: The endpoint's response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    path = fill_path(path, values)
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return await self.client.request(
      method, path, params=values, validator=response_validator, validate=validate
    )
