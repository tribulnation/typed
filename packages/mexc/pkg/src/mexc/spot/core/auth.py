from typing_extensions import Any, Mapping
from dataclasses import dataclass, field
from urllib.parse import urlencode, quote
import hashlib
import hmac
import httpx
from mexc.core import AuthError
from mexc.core.http import HttpClient, HttpMixin

def sign(payload: str, *, secret: str) -> str:
  return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

def signed_query(params: Mapping, *, secret: str) -> str:
  def fix(v):
    # fix bools, which would show otherwise as "hello=True" instead of "hello=true"
    if isinstance(v, bool):
      return str(v).lower()
    else:
      return v
  fixed_params = [(k, fix(v)) for k, v in params.items()]
  query = urlencode(fixed_params, quote_via=quote)
  return query + '&signature=' + sign(query, secret=secret)

@dataclass(kw_only=True)
class AuthHttpClient(HttpClient):
  api_key: str
  api_secret: str = field(repr=False)
  public: bool = field(default=False, repr=False)

  @property
  def headers(self) -> dict:
    return { 'X-MEXC-APIKEY': self.api_key }

  def signed_query(self, params: Mapping) -> str:
    self.require_auth()
    return signed_query(params, secret=self.api_secret)

  def require_auth(self):
    if self.public or not self.api_key or not self.api_secret:
      raise AuthError('MEXC API credentials are required for authenticated endpoints.')
  
  async def authed_request(
    self, method: str, path: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: Any | None = None,
    params: Mapping | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: httpx._types.AuthTypes | httpx._client.UseClientDefault | None = httpx.USE_CLIENT_DEFAULT,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    self.require_auth()
    headers = {**self.headers, **(headers or {})}
    return await self.request(
      method, path, headers=headers, params=params, json=json,
      content=content, data=data, files=files, auth=auth,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions,
    )
  
  async def signed_request(
    self, method: str, path: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: Any | None = None,
    params: Mapping | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: httpx._types.AuthTypes | httpx._client.UseClientDefault | None = httpx.USE_CLIENT_DEFAULT,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    self.require_auth()
    path = path + '?' + self.signed_query(params or {})
    return await self.authed_request(
      method, path, headers=headers, json=json,
      content=content, data=data, files=files, auth=auth,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions,
    )
  
@dataclass
class AuthHttpMixin(HttpMixin):
  base_url: str = field(kw_only=True)
  auth_http: AuthHttpClient

  @classmethod
  def new(cls, api_key: str, api_secret: str, *, base_url: str):
    """Create a mixin from a single `AuthHttpClient`, shared by `http` and `auth_http`
    so an unauthenticated `request()` (inherited from `HttpMixin`) and a signed one go
    through the same underlying transport."""
    client = AuthHttpClient(api_key=api_key, api_secret=api_secret)
    return cls(base_url=base_url, http=client, auth_http=client)
  
  async def __aenter__(self):
    await self.auth_http.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.auth_http.__aexit__(exc_type, exc_value, traceback)

  async def authed_request(
    self, method: str, path: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: Any | None = None,
    params: Mapping | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: httpx._types.AuthTypes | httpx._client.UseClientDefault | None = httpx.USE_CLIENT_DEFAULT,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    return await self.auth_http.authed_request(
      method, self.base_url + path, headers=headers, json=json,
      content=content, data=data, files=files, auth=auth,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions, params=params,
    )
  
  async def signed_request(
    self, method: str, path: str,
    *,
    content: httpx._types.RequestContent | None = None,
    data: httpx._types.RequestData | None = None,
    files: httpx._types.RequestFiles | None = None,
    json: Any | None = None,
    params: Mapping | None = None,
    headers: Mapping[str, str] | None = None,
    cookies: httpx._types.CookieTypes | None = None,
    auth: httpx._types.AuthTypes | httpx._client.UseClientDefault | None = httpx.USE_CLIENT_DEFAULT,
    follow_redirects: bool | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    timeout: httpx._types.TimeoutTypes | httpx._client.UseClientDefault = httpx.USE_CLIENT_DEFAULT,
    extensions: httpx._types.RequestExtensions | None = None,
  ):
    return await self.auth_http.signed_request(
      method, self.base_url + path, headers=headers, json=json,
      content=content, data=data, files=files, auth=auth,
      follow_redirects=follow_redirects, cookies=cookies,
      timeout=timeout, extensions=extensions, params=params,
    )
