"""HTTP transport: Kraken Spot REST client, owning connection, HMAC-SHA512
authentication and validation.
"""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field
from urllib.parse import urlencode
import json as json_module

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.validation import TypedDict, validator
import httpx

from ..endpoint.rpc import RpcClient
from ..auth import AuthResult, Credentials, NonceGenerator, sign
from ..envelope import raise_http_status, unwrap

T = TypeVar('T')

SPOT_API_URL = 'https://api.kraken.com'


class GetWebSocketsTokenResult(TypedDict):
  """Result of `POST /0/private/GetWebSocketsToken`."""

  token: str
  expires: int
  """Seconds after which the token expires (~900)."""


validate_ws_token = validator(GetWebSocketsTokenResult)


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """Kraken Spot REST client. Public endpoints are unsigned GETs; private endpoints
  are signed, form-urlencoded POSTs -- see `auth.sign`.
  """

  base_url: str = SPOT_API_URL
  http: HttpClient = field(default_factory=HttpClient)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only public endpoints can be called."""
  validate: bool = True
  nonce: NonceGenerator = field(default_factory=NonceGenerator)

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def request(
    self,
    path: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned GET request to `base_url + path`."""
    response = await self.http.request('GET', self.base_url + path, params=params)
    return self.result(response, validator=validator, validate=validate)

  async def authed_request(
    self,
    path: str,
    data: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send a POST request to a private endpoint. Signs the exact bytes that
    get sent, not a reconstruction of them: the form body is url-encoded once, and that
    same string is both hashed into the signature and sent as the request content.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    nonce = await self.nonce.next()
    encoded_body = urlencode({'nonce': nonce, **(data or {})})
    signature = sign(path, nonce, encoded_body, self.credentials.private_key)
    headers = {
      'API-Key': self.credentials.api_key,
      'API-Sign': signature,
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = await self.http.request(
      'POST', self.base_url + path, content=encoded_body, headers=headers
    )
    return self.result(response, validator=validator, validate=validate)

  async def authed_json_request(
    self,
    path: str,
    data: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send a POST request with a JSON body, for the two endpoints Kraken
    rejects a form-urlencoded body on (`AddOrderBatch`, `CancelOrderBatch` -- see
    `spec/status.md`). Signs the exact JSON bytes sent, same as `authed_request` does
    for its form body.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    nonce = await self.nonce.next()
    encoded_body = json_module.dumps({'nonce': nonce, **(data or {})})
    signature = sign(path, nonce, encoded_body, self.credentials.private_key)
    headers = {
      'API-Key': self.credentials.api_key,
      'API-Sign': signature,
      'Content-Type': 'application/json',
    }
    response = await self.http.request(
      'POST', self.base_url + path, content=encoded_body, headers=headers
    )
    return self.result(response, validator=validator, validate=validate)

  async def authed_raw_request(
    self,
    path: str,
    data: Mapping[str, Any] | None = None,
    *,
    validate: bool | None = None,
  ) -> bytes:
    """Sign and send a POST request to a private endpoint whose response is not the
    standard `{error, result}` JSON envelope (`RetrieveExport`'s binary export file) --
    returns the raw response body, unparsed and unvalidated.

    `validate` is accepted but unused: a raw binary response has no schema to validate
    against, so there's nothing for it to control (see `RpcClient.authed_raw_request`).

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    nonce = await self.nonce.next()
    encoded_body = urlencode({'nonce': nonce, **(data or {})})
    signature = sign(path, nonce, encoded_body, self.credentials.private_key)
    headers = {
      'API-Key': self.credentials.api_key,
      'API-Sign': signature,
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = await self.http.request(
      'POST', self.base_url + path, content=encoded_body, headers=headers
    )
    if not response.is_success:
      raise_http_status(response)
    return response.content

  async def get_ws_token(self) -> AuthResult:
    """Fetch a fresh WebSocket auth token (`GetWebSocketsToken`, ~900s TTL), adapted to
    the shared `AuthResult` shape `auth.TokenCache` expects.
    """
    result = await self.authed_request(
      '/0/private/GetWebSocketsToken', validator=validate_ws_token
    )
    return {'access_token': result['token'], 'expires_in': result['expires']}

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap the envelope and map errors, then validate."""
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload
