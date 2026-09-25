"""Deposit bridge core (`client.deposit_bridge`): universal deposit addresses on
`bridge.lighter.xyz`, with its own `x-api-key` credential and `{errorCode, errorMsg}` errors.

JSON bodies in, bare JSON out. Error codes: `InvalidParameterError` (400),
`InsufficientPermissionError` (403: missing or invalid key, or a wallet this key did not
generate an address for), `DependencyFailureError` (502, retryable).
"""

from typing_extensions import Any, Literal, Self, TypeVar
from dataclasses import dataclass, field
from types import UnionType

from typed_core.http import HttpClient
from typed_core.validation import validator
import httpx

from ..core.endpoint.wire import dump_request, fill_path
from ..core.exc import ApiError, AuthError, BadRequest, RateLimited
from ..core.networks import BRIDGE_URL

T = TypeVar('T')


@dataclass(kw_only=True)
class BridgeClient:
  """HTTP client for the deposit bridge."""

  base_url: str = BRIDGE_URL
  """Bridge base URL."""
  api_key: str | None = field(default=None, repr=False)
  """Builder `x-api-key`; `None` means every call raises `AuthError`."""
  api_key_variable: str = 'LIGHTER_BRIDGE_API_KEY'
  """Environment variable the key is read from, named in the `AuthError` when it is missing."""
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

    Errors carry `(status, message, payload)`; the bridge's `errorCode` name stays in
    `payload`.

    Raises:
      AuthError: `InsufficientPermissionError` (403).
      RateLimited: Status 429.
      BadRequest: `InvalidParameterError`, or any other 4xx.
      ApiError: `DependencyFailureError` (502), or any other 5xx.
    """
    try:
      payload: Any = response.json()
    except ValueError:
      payload = response.text[:500]
    if response.is_success:
      return payload
    code = payload.get('errorCode') if isinstance(payload, dict) else None
    message = str(payload.get('errorMsg', '') if isinstance(payload, dict) else payload)
    status = response.status_code
    if status == 403 or code == 'InsufficientPermissionError':
      raise AuthError(status, message, payload)
    if status == 429:
      raise RateLimited(status, message, payload)
    if 400 <= status < 500:
      raise BadRequest(status, message, payload)
    raise ApiError(status, message, payload)

  async def request(
    self,
    method: Literal['GET', 'POST'],
    path: str,
    *,
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request with the `x-api-key` header, then validate.

    Args:
      method: HTTP verb.
      path: URL path.
      json: JSON body.
      validator: Response validator.
      validate: Per-call override of response validation.

    Raises:
      AuthError: No bridge API key was configured.
    """
    if self.api_key is None:
      raise AuthError(
        'The deposit bridge needs an API key: pass `bridge_api_key` or set '
        f'{self.api_key_variable}.'
      )
    response = await self.http.request(
      method, self.base_url + path, json=json, headers={'x-api-key': self.api_key}
    )
    payload = self.result(response)
    should_validate = self.validate if validate is None else validate
    if validator is not None and should_validate:
      return validator.python(payload)
    return payload


@dataclass(kw_only=True, frozen=True)
class BridgeEndpoint:
  """Base class for deposit bridge endpoints."""

  client: BridgeClient
  """The bridge transport."""

  async def __aenter__(self) -> Self:
    """Return this surface; the bridge transport opens lazily, on first use.

    Entering or leaving it with `async with` opens and closes nothing: the transport is shared
    with sibling surfaces, and only the root client (`core.client.ClientBase`) closes it.
    """
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client closes the bridge transport, which sibling surfaces
    may still be using."""

  async def request(
    self,
    request: Any = None,
    *,
    method: Literal['GET', 'POST'],
    path: str,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one bridge call: path placeholders from `request`, the rest as a JSON body.

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
      method,
      path,
      json=values if values and method != 'GET' else None,
      validator=response_validator,
      validate=validate,
    )
