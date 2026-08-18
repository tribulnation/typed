from typing_extensions import Any, Mapping
from dataclasses import dataclass, field
import asyncio
import os
import httpx

from typed_core.exceptions import NetworkError

def _default_limits() -> httpx.Limits:
  if os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY'):
    return httpx.Limits(max_keepalive_connections=0)
  return httpx.Limits()

@dataclass
class HttpClient:
  """Managed HTTP client, wrapping `httpx.AsyncClient`.

  ### Concurrency Contract
  1. Connection: single owner via `async with`, also supports lazy no-owner use
  2. Requests: many concurrent callers OK
  """
  limits: httpx.Limits = field(default_factory=_default_limits)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)
  _client: httpx.AsyncClient | None = None

  @property
  async def client(self) -> httpx.AsyncClient:
    async with self.lock:
      if self._client is None:
        self._client = await httpx.AsyncClient(limits=self.limits).__aenter__()
      return self._client

  async def __aenter__(self):
    """Take ownership without connecting; the underlying client opens lazily on first use."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    async with self.lock:
      if self._client is not None:
        await self._client.__aexit__(exc_type, exc_value, traceback)
        self._client = None

  async def request(
    self, method: str, url: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: Any | None = None,
    params: Mapping[str, Any] | None = None,
    headers: Mapping | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: httpx._types.AuthTypes | httpx._client.UseClientDefault | None = httpx.USE_CLIENT_DEFAULT,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    try:
      client = await self.client
      return await client.request(
        method, url, params=params, cookies=cookies, json=json,
        content=content, data=data, files=files, auth=auth, follow_redirects=follow_redirects,
        timeout=timeout, extensions=extensions,
        headers=headers,
      )
    except httpx.HTTPError as e:
      req = f'{method} {url}'
      raise NetworkError(f'Error sending request to {req}', *e.args) from e
