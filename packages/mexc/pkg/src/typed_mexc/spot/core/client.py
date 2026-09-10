"""Spot's raw REST transport: connection, and MEXC's query-string HMAC-SHA256 signing.
Every signed Spot call -- GET or POST alike -- sends its full field set (including a
freshly computed `timestamp`) as one signed query string with an empty body; confirmed
live, no Spot endpoint takes a real JSON body on the wire (`spot.trade.place_order`'s
own discriminated order fields travel the same signed-query-string way).
"""

from typing_extensions import Any, Mapping, Self, TypeVar
from dataclasses import dataclass, field
from urllib.parse import quote, urlencode

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.validation import validator

from ...core.auth import Credentials, sign
from ...core.types import timestamp_millis
from .envelope import unwrap

T = TypeVar('T')

MEXC_SPOT_API_BASE = 'https://api.mexc.com'


def _fix(value: Any) -> Any:
  """MEXC's query encoding expects a lowercase `true`/`false`, not Python's `True`/`False`."""
  return str(value).lower() if isinstance(value, bool) else value


def signed_query(params: Mapping[str, Any], *, secret: str) -> str:
  """Build one signed Spot query string: every field URL-encoded in declaration
  order, followed by a `signature` computed over that exact string.

  Args:
    params: Every field going on the wire, `timestamp` included.
    secret: The account's API secret.
  """
  query = urlencode([(k, _fix(v)) for k, v in params.items()], quote_via=quote)
  return query + '&signature=' + sign(query, secret=secret)


@dataclass(kw_only=True, frozen=True)
class SpotHttpClient:
  """Spot's REST client -- public endpoints are unsigned; private endpoints sign the
  full field set as one query string, sent with every HTTP method."""

  base_url: str = MEXC_SPOT_API_BASE
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
    self, method: str, path: str, params: Mapping[str, Any] | None = None, *,
    validator: 'validator[T] | None' = None, validate: bool | None = None,
  ) -> T:
    """Send an unsigned request to a public endpoint."""
    response = await self.http.request(method, self.base_url + path, params=params)
    return self._result(response, validator=validator, validate=validate)

  async def authed_request(
    self, method: str, path: str, params: Mapping[str, Any] | None = None, *,
    validator: 'validator[T] | None' = None, validate: bool | None = None,
  ) -> T:
    """Sign and send a request to a private endpoint -- every field, including a
    freshly computed `timestamp`, travels as one signed query string.

    Args:
      method: Wire HTTP verb.
      path: Path relative to `base_url`.
      params: Caller-declared fields (never `timestamp`/`signature` -- both are
        computed here, exactly once, so the same value backs both the signed string
        and the signature over it).
      validator: Validates the decoded payload when validation is enabled.
      validate: Per-call override of response validation.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    values = {**(params or {}), 'timestamp': timestamp_millis.now()}
    query = signed_query(values, secret=self.credentials.api_secret)
    headers = {'X-MEXC-APIKEY': self.credentials.api_key}
    response = await self.http.request(method, f'{self.base_url}{path}?{query}', headers=headers)
    return self._result(response, validator=validator, validate=validate)

  def _result(self, response, *, validator: 'validator[T] | None', validate: bool | None) -> T:
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload  # type: ignore
