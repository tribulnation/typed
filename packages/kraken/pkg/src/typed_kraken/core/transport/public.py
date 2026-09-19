"""Managed unsigned HTTP transport shared by Futures and chart clients."""

from dataclasses import dataclass, field
from typing_extensions import Any, Mapping, Self, TypeVar
import httpx

from typed_core.http import HttpClient
from typed_core.validation import validator

from ..envelope import raise_http_status

T = TypeVar('T')
validate_json = validator(object)


@dataclass(kw_only=True)
class PublicHttpClient:
  """Own an unsigned connection and validate public response payloads."""

  base_url: str = 'https://futures.kraken.com'
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  async def __aenter__(self) -> Self:
    """Acquire the managed connection without opening it eagerly."""
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close any connection opened by requests."""
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def payload(self, response: httpx.Response) -> Any:
    """Parse a JSON response after translating HTTP failures."""
    if not response.is_success:
      raise_http_status(response)
    return validate_json(response.text)

  async def request(
    self,
    path: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send a public GET, translate failures and validate the endpoint payload."""
    response = await self.http.request(
      'GET', self.base_url.rstrip('/') + path, params=params
    )
    payload = self.payload(response)
    if validator is not None and (self.validate if validate is None else validate):
      return validator.python(payload)
    return payload
