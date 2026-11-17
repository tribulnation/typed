"""Signed Kraken Futures REST transport."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing_extensions import Any, Literal, Mapping, Sequence, TypeVar
from urllib.parse import urlencode
import json

from typed_core.exceptions import AuthError
from typed_core.validation import validator

from ..core.auth import NonceGenerator
from ..futures.core import FuturesHttpClient
from .auth import FuturesCredentials, sign_request

T = TypeVar('T')

FUTURES_URL = 'https://futures.kraken.com'
DEMO_FUTURES_URL = 'https://demo-futures.kraken.com'
"""The demo environment; Kraken announced its shutdown in 2026, so it may not answer."""


def wire(value: Any) -> str:
  """A parameter as Kraken reads it: booleans in lowercase, numbers in plain notation."""
  if isinstance(value, bool):
    return 'true' if value else 'false'
  if isinstance(value, Decimal):
    return f'{value.normalize():f}'
  return str(value)


Params = Mapping[str, Any] | Sequence[tuple[str, Any]]
"""Query parameters: a mapping, or pairs where a key repeats (`orderIds=a&orderIds=b`)."""


def encode(params: Params | None) -> str:
  """URL-encode `params` in order, skipping `None` values."""
  pairs = params.items() if isinstance(params, Mapping) else params or ()
  return urlencode([(key, wire(value)) for key, value in pairs if value is not None])


@dataclass(kw_only=True)
class SignedFuturesHttpClient(FuturesHttpClient):
  """Futures REST with `APIKey`/`Nonce`/`Authent` headers on private calls.

  Parameters go in the query string, which is what gets signed, for every method
  except `batchorder`, whose `json=` form body is signed instead. Both are signed
  URL-encoded exactly as sent, the scheme Kraken requires since its October 2025
  change (hashing decoded parameters is phased out).
  """

  credentials: FuturesCredentials | None = None
  nonces: NonceGenerator = field(default_factory=NonceGenerator)

  async def signed(
    self,
    method: Literal['GET', 'POST', 'PUT'],
    path: str,
    params: Params | None = None,
    *,
    body: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one signed request and validate its payload.

    Args:
      method: HTTP method.
      path: Full API path, e.g. `/derivatives/api/v3/sendorder`.
      params: Query parameters, signed.
      body: A JSON document sent as the `json=` form body and signed instead of the
        query (batch orders).
      validator: Validates the payload.
      validate: Override the client's validation default for this call.

    Raises:
      AuthError: The client has no credentials, or the venue refused them.
    """
    if self.credentials is None:
      raise AuthError('This Kraken Futures client has no credentials')
    query = encode(params)
    content = None
    if body is not None:
      content = urlencode(
        {'json': json.dumps(body, separators=(',', ':'), default=float)}
      )
    nonce = str(await self.nonces.next())
    headers = {
      'APIKey': self.credentials.api_key,
      'Nonce': nonce,
      'Authent': sign_request(
        path=path,
        post_data=content if content is not None else query,
        nonce=nonce,
        private_key=self.credentials.private_key,
      ),
      'Content-Type': 'application/x-www-form-urlencoded',
    }
    url = self.base_url.rstrip('/') + path + (f'?{query}' if query else '')
    response = await self.http.request(method, url, content=content, headers=headers)
    payload = self.payload(response)
    if validator is not None and (self.validate if validate is None else validate):
      return validator.python(payload)
    return payload
