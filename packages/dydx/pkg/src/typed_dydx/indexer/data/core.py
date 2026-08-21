"""Shared dYdX indexer transport primitives."""

from typing_extensions import Any, Mapping, Protocol, Self, TypeVar
from dataclasses import dataclass, field
import pydantic
import httpx

from typed_core import HttpClient, ApiError
from typed_core.exceptions import BadRequest, RateLimited
from typed_core.util import path_join

T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)

class ResponseParser(Protocol[T_co]):
  """Response parser with per-call validation control."""

  def __call__(self, r: httpx.Response, *, validate: bool = True) -> T_co:
    """Parse an HTTP response."""
    ...

def response_parser(type: type[T]) -> ResponseParser[T]:
  """Build a response parser for an indexer response type.

  Args:
    type: Response type to validate against.

  Returns:
    A parser function for the response type.
  """
  adapter = pydantic.TypeAdapter(type)
  def parse_response(r: httpx.Response, *, validate: bool = True) -> T:
    """Parse and validate an indexer HTTP response.
  
    Args:
      r: HTTP response.
      validate: Override the client response validation default for this call.
  
    Returns:
      The parsed response payload.
    """
    if r.status_code == 200:
      return adapter.validate_json(r.text) if validate else r.json()
    elif r.status_code == 429:
      raise RateLimited(r.status_code, r.json())
    elif 400 <= r.status_code < 500:
      raise BadRequest(r.status_code, r.json())
    else:
      raise ApiError(r.status_code, r.json())
  return parse_response

INDEXER_HTTP_URL = 'https://indexer.dydx.trade/'
INDEXER_TESTNET_HTTP_URL = 'https://indexer.v4testnet.dydx.exchange'

@dataclass(kw_only=True)
class IndexerMixin:
  """Shared HTTP indexer endpoint mixin."""
  url: str = INDEXER_HTTP_URL
  client: HttpClient = field(default_factory=HttpClient)
  default_validate: bool = True

  def validate(self, validate: bool | None = None) -> bool:
    """Resolve a per-call validation override.
  
    Args:
      validate: Override the client response validation default for this call.
  
    Returns:
      The effective validation setting.
    """
    return self.default_validate if validate is None else validate

  async def __aenter__(self) -> Self:
    """Enter the indexer client context.
  
    Returns:
      The configured indexer client.
    """
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Exit the indexer client context."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self, method: str, path: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: Any | None = None,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: httpx._types.AuthTypes | httpx._client.UseClientDefault | None = httpx.USE_CLIENT_DEFAULT,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ) -> httpx.Response:
    """Send an HTTP request to the indexer.
  
    Args:
      method: HTTP method.
      path: Indexer path.
      content: Request body content.
      data: Form data.
      files: Multipart files.
      json: JSON request body.
      params: Query parameters.
      headers: Request headers.
      cookies: Request cookies.
      auth: Request authentication override.
      follow_redirects: Redirect handling override.
      timeout: Request timeout override.
      extensions: Request extensions.
  
    Returns:
      The raw HTTP response.
    """
    url = path_join(self.url, path)
    return await self.client.request(
      method, url, params=params, cookies=cookies, json=json,
      content=content, data=data, files=files, auth=auth, follow_redirects=follow_redirects,
      timeout=timeout, extensions=extensions,
      headers=headers,
    )
