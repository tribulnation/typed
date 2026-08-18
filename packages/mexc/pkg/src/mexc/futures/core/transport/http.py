"""Futures HTTP transport: connection, signing and envelope handling for the RPC surface."""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field
import json as _json

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.times import EpochConverter
from typed_core.validation import validator
import httpx

from ....core.auth import Credentials
from ....core.endpoint.rpc import RpcClient
from ..auth import sign, query_string
from ..envelope import unwrap

T = TypeVar('T')

MEXC_FUTURES_API_BASE = 'https://contract.mexc.com'

request_time = EpochConverter.milliseconds()
"""Millisecond epoch clock for the `Request-Time` signing header."""


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """Futures HTTP RPC client, owning connection, authentication and validation."""

  base_url: str = MEXC_FUTURES_API_BASE
  http: HttpClient = field(default_factory=HttpClient)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only public endpoints can be called."""
  validate: bool = True

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
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request to `base_url + path`."""
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
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request.

    Futures signs `accessKey + Request-Time + requestParamString` -- the
    dictionary-sorted query string for GET/DELETE, or the raw JSON body string for
    POST -- and carries the result in three headers rather than the query string
    itself.

    Raises:
      AuthError: This client was built with no credentials.
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    t = request_time.now()
    if json is not None:
      body = _json.dumps(json, separators=(',', ':'))
      signed_part = body
    else:
      body = None
      signed_part = query_string(params) if params else ''
    signature = sign(f'{self.credentials.api_key}{t}{signed_part}', secret=self.credentials.api_secret)
    headers = {
      'ApiKey': self.credentials.api_key,
      'Request-Time': str(t),
      'Signature': signature,
      **({'Content-Type': 'application/json'} if json is not None else {}),
    }
    response = await self.http.request(
      method, self.base_url + path, params=params, content=body, headers=headers
    )
    return self.result(response, validator=validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap the envelope and map errors, then validate. Futures keeps the whole
    envelope (see `envelope.py`), not just `data` -- generated pagination reads fields
    like `totalPage` that sit beside it.
    """
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload
