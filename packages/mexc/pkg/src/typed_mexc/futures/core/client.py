"""Futures' raw REST transport: connection, and MEXC's header-based HMAC-SHA256
signing. Unlike Spot, every signed Futures call carries its fields in the real HTTP
verb's usual place -- a query string for `GET`/`DELETE`, a JSON body for `POST` -- and
signs `apiKey + timestamp + (query or body)` into three headers (`ApiKey`,
`Request-Time`, `Signature`), never a wire query/body field of their own.
"""

from typing_extensions import Any, Mapping, Self, TypeVar
from dataclasses import dataclass, field
from urllib.parse import quote
import json as json_module

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.validation import validator

from ...core.auth import Credentials, sign
from ...core.types import timestamp_millis
from .envelope import unwrap

T = TypeVar('T')

MEXC_FUTURES_API_BASE = 'https://contract.mexc.com'


def _fix(value: Any) -> Any:
  """MEXC's query encoding expects a lowercase `true`/`false`, not Python's `True`/`False`."""
  return str(value).lower() if isinstance(value, bool) else value


def query_string(params: Mapping[str, Any]) -> str:
  """Build Futures' signed query string: every field sorted by name and URL-encoded --
  confirmed live, unlike Spot's own insertion-order query string."""
  return '&'.join(f'{k}={quote(str(_fix(v)))}' for k, v in sorted(params.items()))


@dataclass(kw_only=True, frozen=True)
class FuturesHttpClient:
  """Futures' REST client -- public endpoints are unsigned; private endpoints sign a
  query string (`GET`/`DELETE`) or a JSON body (`POST`), always via the same three
  headers."""

  base_url: str = MEXC_FUTURES_API_BASE
  http: HttpClient = field(default_factory=HttpClient)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only public endpoints can be called."""
  validate: bool = True

  def should_validate(self, validate: bool | None = None) -> bool:
    """Resolve a per-call validation override against the client default."""
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self, method: str, path: str, params: 'Mapping[str, Any] | list[Any] | None' = None, *,
    validator: 'validator[T] | None' = None, validate: bool | None = None,
  ) -> T:
    """Send an unsigned request to a public endpoint."""
    if method == 'POST':
      response = await self.http.request(method, self.base_url + path, json=params)
    else:
      assert not isinstance(params, list), (
        'a raw JSON-array body only ever travels as a POST body -- no MEXC endpoint '
        'sends one as a query string'
      )
      response = await self.http.request(method, self.base_url + path, params=params)
    return self._result(response, validator=validator, validate=validate)

  async def authed_request(
    self, method: str, path: str, params: 'Mapping[str, Any] | list[Any] | None' = None, *,
    validator: 'validator[T] | None' = None, validate: bool | None = None,
  ) -> T:
    """Sign and send a request to a private endpoint: `params` travels as a sorted
    query string for `GET`/`DELETE`, or a compact JSON body for `POST`.

    Args:
      method: Wire HTTP verb.
      path: Path relative to `base_url`, placeholders already substituted.
      params: Every field going on the wire.
      validator: Validates the decoded payload when validation is enabled.
      validate: Per-call override of response validation.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    ts = timestamp_millis.now()
    if method == 'POST':
      body = json_module.dumps(params, separators=(',', ':')) if params else ''
      signature = sign(f'{self.credentials.api_key}{ts}{body}', secret=self.credentials.api_secret)
      headers = self._headers(timestamp=ts, signature=signature)
      headers['Content-Type'] = 'application/json'
      response = await self.http.request(
        method, self.base_url + path, headers=headers, content=body,
      )
    else:
      assert not isinstance(params, list), (
        'a raw JSON-array body only ever travels as a POST body -- no MEXC endpoint '
        'sends one as a query string'
      )
      query = query_string(params) if params else ''
      signature = sign(f'{self.credentials.api_key}{ts}{query}', secret=self.credentials.api_secret)
      headers = self._headers(timestamp=ts, signature=signature)
      url = self.base_url + path + (f'?{query}' if query else '')
      response = await self.http.request(method, url, headers=headers)
    return self._result(response, validator=validator, validate=validate)

  def _headers(self, *, timestamp: int, signature: str) -> dict[str, str]:
    assert self.credentials is not None
    return {
      'ApiKey': self.credentials.api_key,
      'Request-Time': str(timestamp),
      'Signature': signature,
    }

  def _result(self, response, *, validator: 'validator[T] | None', validate: bool | None) -> T:
    envelope = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(envelope)
    return envelope  # type: ignore
