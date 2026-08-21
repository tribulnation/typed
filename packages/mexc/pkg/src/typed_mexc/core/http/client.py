from dataclasses import dataclass, field
from typing_extensions import Any, Mapping
import httpx

from typed_core.http import HttpClient

__all__ = ['HttpClient', 'HttpMixin']

@dataclass
class HttpMixin:
  base_url: str = field(kw_only=True)
  http: HttpClient = field(kw_only=True, default_factory=HttpClient)

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self, method: str, path: str,
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
    return await self.http.request(
      method,
      self.base_url + path,
      params=params,
      headers=headers,
      cookies=cookies,
      json=json,
      content=content,
      data=data,
      files=files,
      auth=auth,
      follow_redirects=follow_redirects,
      timeout=timeout,
      extensions=extensions,
    )
