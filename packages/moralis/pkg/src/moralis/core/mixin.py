"""Shared Moralis HTTP endpoint primitives."""

from dataclasses import dataclass, field
import os

import httpx
from pydantic import TypeAdapter
from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.http import HttpClient
from typing_extensions import Any, Mapping, TypedDict, get_type_hints


MORALIS_API_URL = 'https://deep-index.moralis.io/api/v2.2'
MORALIS_USER_AGENT = (
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
  '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
)


class MoralisErrorPayload(TypedDict, total=False):
  """Moralis API error payload."""
  message: str
  """Human-readable error description."""
  code: str
  """Moralis error code, when provided."""
  details: str
  """Additional upstream error details."""


error_payload_adapter = TypeAdapter(MoralisErrorPayload)


def env_api_key(api_key: str | None = None) -> str:
  """Return the explicit API key or load `MORALIS_API_KEY`."""
  if api_key is not None:
    return api_key
  try:
    return os.environ['MORALIS_API_KEY']
  except KeyError as exc:
    raise AuthError(
      401,
      {
        'error': 'missing_api_key',
        'message': 'Either provide `api_key` or set MORALIS_API_KEY.',
      },
    ) from exc


def clean_params(params: Mapping[str, Any]) -> dict[str, Any]:
  """Remove unset query parameters before sending a request."""
  return {key: value for key, value in params.items() if value is not None}


@dataclass(kw_only=True)
class Endpoint:
  """Base Moralis endpoint with shared HTTP transport and validation defaults."""
  base_url: str
  api_key: str = field(repr=False)
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  def should_validate(self, validate_param: bool | None = None) -> bool:
    """Resolve per-call validation override against the client default."""
    return self.validate if validate_param is None else validate_param

  async def __aenter__(self):
    """Open the shared HTTP transport."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the shared HTTP transport."""
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def headers(self) -> dict[str, str]:
    """Build Moralis request headers."""
    return {
      'accept': 'application/json',
      'User-Agent': MORALIS_USER_AGENT,
      'X-API-Key': self.api_key,
    }

  async def request(
    self, method: str, path: str, /, *,
    params: Mapping[str, Any] | None = None,
  ) -> httpx.Response:
    """Send an HTTP request relative to the Moralis base URL."""
    response = await self.http.request(
      method,
      f'{self.base_url}{path}',
      params=params,
      headers=self.headers(),
    )
    if response.status_code != 200:
      self.raise_error(response)
    return response

  def raise_error(self, response: httpx.Response):
    """Raise a typed exception for an unsuccessful HTTP response."""
    try:
      payload: Any = error_payload_adapter.validate_json(response.text)
    except Exception:
      try:
        payload = response.json()
      except Exception:
        payload = response.text
    self.raise_api_error(response.status_code, payload)

  def raise_api_error(self, status_code: int, payload: Any):
    """Map Moralis error payloads to shared typed-core exceptions."""
    if status_code in {401, 403}:
      raise AuthError(status_code, payload)
    if status_code == 429:
      raise RateLimited(status_code, payload)
    if 400 <= status_code < 500:
      raise BadRequest(status_code, payload)
    raise ApiError(status_code, payload)


class Router(Endpoint):
  """Router that instantiates typed child endpoint groups."""

  def __init__(
    self, *,
    base_url: str,
    api_key: str,
    http: HttpClient | None = None,
    validate: bool = True,
  ):
    """Create a router and wire its annotated endpoint children."""
    super().__init__(
      base_url=base_url,
      api_key=api_key,
      http=http or HttpClient(),
      validate=validate,
    )
    self.__post_init__()

  def __post_init__(self):
    """Instantiate annotated endpoint children with shared client state."""
    for field_name, cls in get_type_hints(type(self)).items():
      if isinstance(cls, type) and issubclass(cls, Endpoint):
        setattr(
          self,
          field_name,
          cls(
            base_url=self.base_url,
            api_key=self.api_key,
            http=self.http,
            validate=self.validate,
          ),
        )
