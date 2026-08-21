"""The `http` surface: one client for Crypto API (v1/v2/v3), Embed API, and Trading
Spot REST, since all three share a host, an auth scheme, and an envelope — see
`spec/core.md`'s Surfaces section.
"""

import time
from dataclasses import dataclass, field
from typing_extensions import Any, Mapping, Self, TypeVar
from urllib.parse import urlencode
import httpx
import orjson

from typed_core.http import HttpClient
from typed_core.exceptions import AuthError
from typed_core.validation import validator

from ..auth import Credentials, auth_headers
from ..exc import raise_http_status

BIT2ME_API_URL = 'https://gateway.bit2me.com'

T = TypeVar('T')


@dataclass(kw_only=True)
class HttpRpcClient:
  """Implements `endpoint.rpc.RpcClient` over Bit2Me's single HTTP host."""

  base_url: str = BIT2ME_API_URL
  http: HttpClient = field(default_factory=HttpClient)
  credentials: Credentials | None = None
  """`None` restricts the client to public endpoints."""
  validate: bool = True

  async def __aenter__(self) -> Self:
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    return self.validate if validate is None else validate

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Unsigned request, for public endpoints."""
    response = await self.http.request(
      method, self.base_url + path, params=params, json=json
    )
    return self.result(response, validator=validator, validate=validate)

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """HMAC-signed request, for authenticated endpoints.

    Raises:
      AuthError: The client holds no credentials.
    """
    if self.credentials is None:
      raise AuthError(
        'This endpoint requires credentials; build the client with `api_key`/`api_secret` rather than `public=True`'
      )
    path_and_query = path if not params else f'{path}?{urlencode(params, doseq=True)}'
    body = orjson.dumps(json).decode() if json is not None else None
    nonce = str(int(time.time() * 1000))
    headers = auth_headers(
      self.credentials, nonce=nonce, path=path_and_query, body=body
    )
    if body is not None:
      headers['Content-Type'] = 'application/json'
    response = await self.http.request(
      method, self.base_url + path, params=params, content=body, headers=headers
    )
    return self.result(response, validator=validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Turn a raw response into a typed result — Bit2Me's success body *is* the
    documented payload, no envelope to unwrap; failure is HTTP status alone."""
    if not response.is_success:
      raise_http_status(response)
    if validator is not None and self.should_validate(validate):
      return validator.json(response.content)
    return response.json()
