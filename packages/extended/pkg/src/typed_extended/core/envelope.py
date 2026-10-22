"""Extended's response envelope, `{status, data, error, pagination}`, and its mapping onto
`typed_core` exceptions.

Success is `status: "OK"`; the core returns `data` (or, for a paginated endpoint, `data`
together with `pagination`, or, for an endpoint whose success carries no `data` at all, the
whole frame). Failure is `status: "ERROR"` with `error: {code, message}`,
or a bare non-2xx status with an empty or non-JSON body (`401` without a valid key, `404`
for an unknown path, a plain-text `429` or an HTML `502` from a proxy), so the HTTP status is
checked first and the body is read only when it is JSON. A `2xx` body that is not JSON is
not a response this client can interpret, and raises `ValidationError`.

A few endpoints answer "nothing here" with a bodiless `404` (a sub-account holding nothing,
an order id the venue does not know). Those declare `not_found`, and that one response
becomes `None` or `[]`; every other `404`, there or anywhere else, still raises.

Numbers are decoded with `Decimal` for non-integers, so a JSON-number price never passes
through a float; integers (including 64-bit ids above 2^63) stay exact `int`s.
"""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from decimal import Decimal
import json

import httpx

from .exc import ApiError, AuthError, BadRequest, RateLimited, ValidationError


EnvelopeMode = Literal['data', 'page', 'frame']
"""What a successful envelope unwraps to: `data` alone, `{data, pagination}` for a paginated
call, or the whole frame for a call whose success carries no `data` (committing a bridge
quote answers a bare `{"status": "OK"}`)."""


NotFound = Literal['none', 'empty']
"""What a bodiless `404` means on an endpoint whose venue sends it for "nothing here": `none`
returns `None` (a zero balance, an unknown order id), `empty` returns `[]` (no spot
balances)."""


class ErrorBody(TypedDict):
  """The `error` of a failed call."""

  code: int | str
  """Numeric error code (`1001` MarketNotFound, ...); the docs' examples also show names."""
  message: NotRequired[str]
  """Human-readable reason."""


class Pagination(TypedDict, total=False):
  """The `pagination` of a paginated call."""

  cursor: int
  """Id of the last item returned; pass it back as `cursor` for the next page."""
  count: int
  """Items on this page."""


class Page(TypedDict):
  """What the core returns for a paginated endpoint: the rows and the cursor to continue."""

  data: Any
  """The page's rows."""
  pagination: NotRequired[Pagination]
  """Cursor and count; absent when the venue sends none."""


AUTH_CODES = frozenset({1100, 1101, 1102, 1500})
"""Invalid Stark public key, signature or vault, and AccountNotSelected."""
SERVER_CODES = frozenset({1006, 1010})
"""UnhandledError and MaintenanceMode: server-side failures, unless the HTTP status says the
request was at fault (a missing required parameter is `400` with code `1006`)."""
AUTH_NAMES = frozenset(
  {
    'Unauthorized',
    'Forbidden',
    'InvalidStarknetPublicKey',
    'InvalidStarknetSignature',
    'InvalidStarknetVault',
    'AccountNotSelected',
  }
)
"""Error names (as some documented examples spell `code`) meaning a credential problem."""
SERVER_NAMES = frozenset({'UnhandledError', 'InternalServerError', 'MaintenanceMode'})
"""Error names meaning a server-side failure."""


def decode(text: str) -> Any:
  """Decode a JSON body, non-integer numbers as `Decimal`.

  Raises:
    ValidationError: The body is not JSON.
  """
  try:
    return json.loads(text, parse_float=Decimal)
  except ValueError as e:
    raise ValidationError(f'Response is not JSON: {text[:200]!r}') from e


def raise_error(status: int, error: Any, payload: Any):
  """Raise the `typed_core` exception for a failed call.

  Args:
    status: HTTP status code.
    error: The envelope's `error` object, if any.
    payload: The full decoded body (or raw text), attached for debugging.

  Raises:
    AuthError: HTTP `401`/`403`, or an invalid Stark key, signature or vault.
    RateLimited: HTTP `429`.
    ApiError: HTTP `5xx`/`451`, or (on a `2xx` error envelope) an unhandled server error
      or maintenance mode.
    BadRequest: Any other `4xx`, or any other error code (unknown market, invalid order, ...).
  """
  code = error.get('code') if isinstance(error, dict) else None
  message = error.get('message', '') if isinstance(error, dict) else ''
  detail = (code, message, payload) if code is not None else (status, payload)
  if status in (401, 403) or code in AUTH_CODES or code in AUTH_NAMES:
    raise AuthError(*detail)
  if status == 429 or code == 'RateLimited':
    raise RateLimited(*detail)
  if status >= 500 or status == 451:
    raise ApiError(*detail)
  if 400 <= status < 500:
    raise BadRequest(*detail)
  if code in SERVER_CODES or code in SERVER_NAMES:
    raise ApiError(*detail)
  raise BadRequest(*detail)


def unwrap(
  response: httpx.Response,
  *,
  envelope: EnvelopeMode = 'data',
  not_found: NotFound | None = None,
) -> Any:
  """Return what a call produced: `data`, `{data, pagination}`, or the whole frame.

  A successful body that is not an envelope (no `status`) is returned whole: the docs show
  bridge config and quote and the referral reads that way, although live they are enveloped
  like every other endpoint.

  Args:
    response: The HTTP response.
    envelope: `data` for bare `data`; `page` to keep the `pagination` beside it, for a
      paginated endpoint; `frame` for the whole successful frame.
    not_found: What a `404` with an empty body means on this endpoint, when the venue sends
      it for "nothing here": `None` or `[]`. Unset, it raises like any other `404`; a `404`
      carrying a body always raises.

  Raises:
    AuthError: Rejected credentials or signature.
    RateLimited: Too many requests.
    BadRequest: The venue rejected the request.
    ApiError: Any other failure.
    ValidationError: A successful body is not JSON.
  """
  text = response.text
  if not response.is_success:
    if not_found is not None and response.status_code == 404 and not text.strip():
      return [] if not_found == 'empty' else None
    try:
      payload = decode(text) if text.strip() else text
    except ValidationError:
      payload = text
    error = payload.get('error') if isinstance(payload, dict) else None
    raise_error(response.status_code, error, payload)
  if not text.strip():
    return {'data': None} if envelope == 'page' else None
  payload = decode(text)
  if not isinstance(payload, dict) or 'status' not in payload:
    return payload
  status: Literal['OK', 'ERROR'] | Any = payload.get('status')
  if status != 'OK':
    raise_error(response.status_code, payload.get('error'), payload)
  if envelope == 'frame':
    return payload
  if envelope == 'page':
    result: Page = {'data': payload.get('data')}
    if (pagination := payload.get('pagination')) is not None:
      result['pagination'] = pagination
    return result
  return payload.get('data')
