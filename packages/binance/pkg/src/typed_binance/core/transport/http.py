"""HTTP transport: one `RpcClient` shared by every Binance REST surface (Spot, USD-M/
COIN-M Futures, Options, Portfolio Margin) — only `base_url` and `credentials` differ per
surface, see `main.py`.
"""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field
import urllib.parse

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.validation import validator
import httpx

from ..auth import Credentials, signed_params
from ..endpoint.rpc import RpcClient
from ..envelope import raise_error

T = TypeVar('T')

BINANCE_API_URL = 'https://api.binance.com'


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """HTTP RPC client, owning connection, authentication and validation."""

  base_url: str = BINANCE_API_URL
  http: HttpClient = field(default_factory=HttpClient)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only `NONE`-security endpoints can be called."""
  recv_window: int | None = None
  """`recvWindow` (ms) sent with every signed request; `None` uses Binance's own 5000ms
  server-side default instead of sending the param at all.
  """
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
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request to `base_url + path`."""
    response = await self.http.request(method, self.base_url + path, params=params)
    return self.result(response, validator=validator, validate=validate)

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request.

    Binance never uses JSON bodies: every param — including `timestamp` and, if set,
    `recvWindow` — is form-encoded into the query string (`GET`/`DELETE`) or the request
    body (`POST`/`PUT`), and the signature covers exactly that encoded string.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    signed = signed_params(params, self.credentials, recv_window=self.recv_window)
    encoded = urllib.parse.urlencode(signed, doseq=True)
    headers = {'X-MBX-APIKEY': self.credentials.api_key}
    if method in ('GET', 'DELETE'):
      response = await self.http.request(
        method, f'{self.base_url}{path}?{encoded}', headers=headers
      )
    else:
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
      response = await self.http.request(
        method, self.base_url + path, content=encoded, headers=headers
      )
    return self.result(response, validator=validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Return the bare JSON body, raising on a non-2XX status.

    Binance's envelope has no success wrapper: a 2XX body *is* the result. Only failure
    responses carry `{code, msg}`, mapped by `envelope.raise_error`.
    """
    if not response.is_success:
      try:
        payload: Any = response.json()
      except ValueError:
        payload = response.text
      raise_error(response.status_code, payload)
    # Some endpoints (e.g. `margin.liquidation_loan` with nothing outstanding) send a 2XX
    # with a genuinely empty body rather than `{}` — `response.json()` raises on that, so
    # treat "no content" as an empty object rather than crashing on a successful response.
    payload = response.json() if response.content else {}
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload
