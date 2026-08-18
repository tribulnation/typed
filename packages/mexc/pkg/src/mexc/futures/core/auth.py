from typing_extensions import Any, Mapping
from dataclasses import dataclass, field
from urllib.parse import quote
import json as jsonlib
import hashlib
import hmac
import os
import httpx

from mexc.core import AuthError, HttpClient, HttpMixin, timestamp

def sign(payload: str, *, secret: str) -> str:
  return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

def query_string(params: Mapping) -> str:
  def fix(v):
    # fix bools, which would show otherwise as "hello=True" instead of "hello=true"
    if isinstance(v, bool):
      return str(v).lower()
    else:
      return v
  return '&'.join([
    f'{k}={quote(str(fix(v)))}'
    for k, v in sorted(params.items())
  ])
  

@dataclass(kw_only=True)
class AuthHttpClient(HttpClient):
  api_key: str
  api_secret: str = field(repr=False)
  public: bool = field(default=False, repr=False)

  def require_auth(self):
    if self.public or not self.api_key or not self.api_secret:
      raise AuthError('MEXC API credentials are required for authenticated endpoints.')

  def headers(self, *, timestamp: int, signature: str) -> dict:
    return {
      'ApiKey': self.api_key,
      'Request-Time': str(timestamp),
      'Signature': signature,
    }

  async def signed_request(
    self, method: str, path: str,
    *,
    params: Mapping | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    """Non-POST request"""
    self.require_auth()
    ts = timestamp.now()
    query = query_string(params) if params else ''
    path = path + '?' + query
    signature = sign(f'{self.api_key}{ts}{query}', secret=self.api_secret)
    headers = {**self.headers(timestamp=ts, signature=signature), **(headers or {})}
    
    return await self.request(
      method, path, headers=headers,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions,
    )
  
  async def signed_post(
    self, path: str,
    *,
    json: Any | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    self.require_auth()
    ts = timestamp.now()
    body = jsonlib.dumps(json) if json else ''
    headers = dict(headers or {})
    
    signature = sign(f'{self.api_key}{ts}{body}', secret=self.api_secret)
    headers = {
      'Content-Type': 'application/json',
      **self.headers(timestamp=ts, signature=signature),
      **(headers or {}),
    }
    return await self.request(
      'POST', path, headers=headers, content=body,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions,
    )
  
@dataclass
class AuthHttpMixin(HttpMixin):
  base_url: str = field(kw_only=True)
  auth_http: AuthHttpClient

  @classmethod
  def new(cls, api_key: str | None = None, api_secret: str | None = None, *, base_url: str):
    """Create a mixin from a single `AuthHttpClient`, shared by `http` and `auth_http`
    so an unauthenticated `request()` (inherited from `HttpMixin`) and a signed one go
    through the same underlying transport."""
    if api_key is None:
      api_key = os.environ['MEXC_ACCESS_KEY']
    if api_secret is None:
      api_secret = os.environ['MEXC_SECRET_KEY']
    client = AuthHttpClient(api_key=api_key, api_secret=api_secret)
    return cls(base_url=base_url, http=client, auth_http=client)
  
  async def __aenter__(self):
    await self.auth_http.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.auth_http.__aexit__(exc_type, exc_value, traceback)

  async def signed_request(
    self, method: str, path: str,
    *,
    params: Mapping | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    return await self.auth_http.signed_request(
      method, self.base_url + path, headers=headers,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions, params=params,
    )
  
  async def signed_post(
    self, path: str,
    *,
    json: Any | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    return await self.auth_http.signed_post(
      self.base_url + path, headers=headers, json=json,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions,
    )
