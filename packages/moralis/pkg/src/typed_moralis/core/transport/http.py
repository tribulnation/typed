"""Moralis REST transport: a single api-key-header auth scheme and a bare-JSON
envelope (the response body on success, an error payload otherwise) shared by every
Moralis product. Only the host varies per product, so one `HttpRpcClient`,
parameterized by `base_url`, backs all of them.
"""

from dataclasses import dataclass, field

import httpx
from pydantic import TypeAdapter
from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.http import HttpClient
from typing_extensions import Any, Mapping, Self, TypedDict

from ..endpoint.rpc import RpcClient


MORALIS_API_URL = 'https://deep-index.moralis.io/api/v2.2'
"""Moralis EVM / Bitcoin / cross-chain ("deep-index") data API base URL."""
MORALIS_SOLANA_API_URL = 'https://solana-gateway.moralis.io'
"""Moralis Solana data API base URL."""
MORALIS_AUTH_API_URL = 'https://authapi.moralis.io'
"""Moralis Auth API base URL (challenge/bind/profile)."""
MORALIS_CORTEX_API_URL = 'https://cortex-api.moralis.io'
"""Moralis Cortex (AI chat) API base URL."""
MORALIS_STREAMS_API_URL = 'https://api.moralis-streams.com'
"""Moralis Streams (webhook management) API base URL."""
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


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """Moralis REST transport backing one product's endpoints (evm, solana, auth, ...)."""

  base_url: str
  api_key: str = field(repr=False)
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  async def __aenter__(self) -> Self:
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
    json: Any | None = None,
  ) -> httpx.Response:
    """Send an HTTP request relative to `base_url`."""
    response = await self.http.request(
      method,
      f'{self.base_url}{path}',
      params=params,
      json=json,
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
