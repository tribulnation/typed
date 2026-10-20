"""GRVT response envelopes and their mapping onto `typed_core` exceptions.

Most gateway (market-data and trading) bodies are `{"result": ...}`, plus `"next"` on
paginated RPCs; an RPC whose response struct has no `result` field answers that struct bare
(`set_derisk_mm_ratio` -> `{"success": true}`), so unwrapping is declared per endpoint
(`Unwrap`). Errors are `{"code", "message", "status"}` over HTTP and `{"code", "message"}` (no
`status`) inside a JSON-RPC `error` over WebSocket, so the WebSocket path recovers the
status from the venue's own code table. Edge bodies are bare JSON, and its errors carry
string codes (`{"code": "err_auth_user_not_logged_in", ...}`) or
`{"status": "failure", "error": ...}`, so they map by HTTP status alone. A non-JSON error
body on either host (a Cloudflare/WAF block page) is never mistaken for a venue auth error.
"""

from typing_extensions import Any, Literal, NoReturn
import json

import httpx

from typed_core.exceptions import (
  ApiError,
  AuthError,
  BadRequest,
  RateLimited,
  ValidationError,
)

Unwrap = Literal['result', 'page', 'none']
"""How much of a gateway body an endpoint returns:

- `result`: the `result` value alone (the default), for an RPC whose response struct has a
  `result` field.
- `page`: the whole `{result, next}` body, for a struct with `result` plus `next`.
- `none`: the body as sent, for any RPC whose response struct has no `result` field
  (`GET /time`, `set_derisk_mm_ratio`, `get_sub_accounts`, ...).
"""

UNAUTHENTICATED = 1000
"""`You need to authenticate prior to using this functionality`: a missing or expired session."""

STATUS_BY_CODE: dict[int, int] = {
  **dict.fromkeys((1000, 1008), 401),
  **dict.fromkeys(
    (
      1001,
      1400,
      2000,
      2001,
      2002,
      2003,
      2004,
      2005,
      2006,
      2007,
      2008,
      2091,
      2141,
      4015,
      4016,
      7701,
    ),
    403,
  ),
  1004: 404,
  **dict.fromkeys((1006, 2090), 429),
  **dict.fromkeys((1002, 1005, 3004, 3005, 3006, 7100, 7103), 500),
  **dict.fromkeys((1009, 1015), 503),
  1014: 504,
}
"""HTTP status of every GRVT error code that is not a `400`, from the venue's own code table
(GRVT's published API spec, `gravity-technologies/api-spec`). WebSocket errors carry no
status, so it is recovered from here; any code missing from this table is a `400`."""

EXCEPTION_BY_CODE: dict[int, type[ApiError]] = {
  2090: BadRequest,
}
"""Codes whose exception class does not follow their HTTP status. `2090` (`Max open orders
exceeded`) is sent as a `429`, but waiting does not clear it; only fills or cancels do. So it
is not a `RateLimited` a caller should retry."""

MAX_UNPARSED_BODY = 500
"""Characters of a non-JSON error body kept on the exception (a block page can be large)."""


def raise_status(status: int, *args: Any) -> NoReturn:
  """Raise the `typed_core` exception matching an HTTP status.

  Args:
    status: HTTP status, sent or recovered from `STATUS_BY_CODE`.
    args: Exception arguments, usually the venue's code, message and full payload.

  Raises:
    AuthError: `401` or `403`: missing session, IP not whitelisted, signer or signature rejected.
      A non-JSON `401`/`403` never reaches here; see `raise_unparsed`.
    RateLimited: `429`: throttled (`1006`).
    BadRequest: Any other `4xx`.
    ApiError: Anything else, including deactivated endpoints (`1009`, `503`).
  """
  if status in (401, 403):
    raise AuthError(*args)
  if status == 429:
    raise RateLimited(*args)
  if 400 <= status < 500:
    raise BadRequest(*args)
  raise ApiError(*args)


def raise_code(
  code: int, message: str, payload: Any, *, status: int | None = None
) -> NoReturn:
  """Raise the exception matching a GRVT error code.

  Args:
    code: GRVT error code.
    message: GRVT error message.
    payload: The full error body or frame, kept for debugging.
    status: HTTP status when the transport sent one; recovered from the code otherwise.

  Raises:
    BadRequest: The code is in `EXCEPTION_BY_CODE` as one (`2090`, max open orders, sent as
      a `429` but not transient).
    AuthError, RateLimited, BadRequest, ApiError: Otherwise, the exception matching the
      code's HTTP status; see `raise_status`.
  """
  if (exc := EXCEPTION_BY_CODE.get(code)) is not None:
    raise exc(code, message, payload)
  raise_status(status or STATUS_BY_CODE.get(code, 400), code, message, payload)


def raise_unparsed(response: httpx.Response, body: Any) -> NoReturn:
  """Raise for an error response whose body is not a JSON venue error (e.g. a block page).

  Venue auth errors are always JSON, so an HTML/text `401`/`403` is a proxy or WAF block
  (GRVT's edge host serves Cloudflare bot challenges to some scripted clients), not bad
  credentials.

  Args:
    response: The error response.
    body: Its decoded body (text, or JSON that is not a venue error object).

  Raises:
    ApiError: A non-JSON `401`/`403`: `(status, "Blocked by ...", text)`.
    RateLimited, BadRequest, ApiError: Any other status, via `raise_status`, as
      `(status, text)`.

  `text` is the body as text (JSON re-encoded), cut to `MAX_UNPARSED_BODY` characters, so
  the second argument is always the message string.
  """
  status = response.status_code
  text = body if isinstance(body, str) else json.dumps(body)
  if len(text) > MAX_UNPARSED_BODY:
    text = text[:MAX_UNPARSED_BODY] + '...'
  if status in (401, 403):
    server = response.headers.get('server', '').lower()
    origin = 'Cloudflare' if server == 'cloudflare' else 'a proxy'
    ray = response.headers.get('cf-ray')
    raise ApiError(
      status, f'Blocked by {origin} (non-JSON {status}, cf-ray={ray})', text
    )
  raise_status(status, status, text)


def decode(response: httpx.Response) -> Any:
  """Decode a JSON body, falling back to the raw text."""
  try:
    return response.json()
  except (json.JSONDecodeError, UnicodeDecodeError):
    return response.text


def check_gateway(response: httpx.Response) -> Any:
  """Return a successful gateway body, or raise its mapped error.

  Args:
    response: A market-data or trading gateway HTTP response.

  Raises:
    AuthError, RateLimited, BadRequest, ApiError: The response is an error; a JSON venue
      error maps via `raise_code`, anything else via `raise_unparsed`.
  """
  body = decode(response)
  if response.is_success:
    return body
  if isinstance(body, dict) and isinstance(code := body.get('code'), int):
    raise_code(code, str(body.get('message', '')), body, status=response.status_code)
  raise_unparsed(response, body)


def check_rpc_frame(frame: dict[str, Any]) -> Any:
  """Return the `result` of a JSON-RPC reply frame, or raise its mapped error.

  Args:
    frame: A decoded JSON-RPC reply (`{"jsonrpc", "result" | "error", "id", "method"}`).

  Raises:
    AuthError, RateLimited, BadRequest, ApiError: The reply carries an `error`; mapped via
      `raise_code`.
  """
  error = frame.get('error')
  if isinstance(error, dict):
    code = error.get('code')
    raise_code(
      code if isinstance(code, int) else 0, str(error.get('message', '')), frame
    )
  return frame.get('result')


def unwrap(body: Any, mode: Unwrap = 'result') -> Any:
  """Strip a gateway success body down to what an endpoint returns.

  Args:
    body: The decoded body (the HTTP body, or a JSON-RPC frame's `result`, which nests it).
    mode: How much of the body to keep.

  Raises:
    ValidationError: `mode` is `result` or `page` and the body has no `result` key.
  """
  if mode == 'none':
    return body
  if not isinstance(body, dict) or 'result' not in body:
    raise ValidationError(f'Expected a {{"result": ...}} body, got: {body!r}')
  return body if mode == 'page' else body['result']


def check_edge(response: httpx.Response) -> Any:
  """Return a successful edge body, or raise the exception matching its HTTP status.

  Args:
    response: An edge HTTP response.

  Raises:
    AuthError, RateLimited, BadRequest, ApiError: The response is an error. A JSON object
      maps by HTTP status via `raise_status`, as `(code, message, body)` with the venue's
      string code (or the status when it is absent, `null` or empty); anything else via
      `raise_unparsed`.
  """
  body = decode(response)
  if response.is_success:
    return body
  if isinstance(body, dict):
    code = body.get('code')
    if code is None or code == '':
      code = response.status_code
    message = str(body.get('message') or body.get('error') or '')
    raise_status(response.status_code, code, message, body)
  raise_unparsed(response, body)
