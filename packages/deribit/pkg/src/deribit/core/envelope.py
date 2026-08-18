"""Deribit's JSON-RPC 2.0 response envelope and its mapping onto `typed_core` exceptions.

Shared by both transports (`transport/http.py`, `transport/ws.py`): HTTP and WebSocket
carry the exact same `{jsonrpc, id, result|error}` shape, so there is exactly one
`unwrap()` rather than one per transport.
"""

from typing_extensions import Any, NotRequired

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.validation import TypedDict, validator


class RpcError(TypedDict):
  """The `error` object of a failed JSON-RPC response."""

  code: int
  """Deribit's own error code, e.g. `10028` for `too_many_requests`."""
  message: str
  """Short machine-readable error message, e.g. `too_many_requests`."""
  data: NotRequired[Any]
  """Optional extra error context."""


class Envelope(TypedDict):
  """Every HTTP and WebSocket response. `result` and `error` are mutually exclusive;
  `testnet`/`usIn`/`usOut`/`usDiff` are per-call diagnostics the core doesn't expose.

  `id` is `NotRequired` for schema leniency, but in practice both transports send one
  and get it echoed back: HTTP's request body carries the same JSON-RPC envelope
  (`{jsonrpc, id, method, params}`) WebSocket always has, now that `transport/http.py`
  sends `POST` with a JSON body rather than a bare `GET`.
  """

  jsonrpc: str
  id: NotRequired[int]
  result: NotRequired[Any]
  error: NotRequired[RpcError]


validate_envelope = validator(Envelope)

AUTH_CODES = frozenset({10000, 10001, 13009, 13010, 13011, 13668})
"""Codes meaning the key, token, signature or 2FA was rejected."""

RATE_LIMIT_CODES = frozenset({10028})
"""Codes meaning the request was throttled (`too_many_requests`)."""

BAD_REQUEST_CODE = 11050
"""`bad_request` — malformed request parameters."""

TRADING_ERROR_RANGE = range(11000, 11010)
"""Order/self-trade errors (`11000`-`11009`) — also malformed/rejected requests, not
server-side failures."""


def raise_error(error: RpcError):
  """Raise the `typed_core` exception matching a JSON-RPC `error` object.

  Args:
    error: The venue's own error object.

  Raises:
    AuthError: Credential, token, signature or 2FA rejection.
    RateLimited: Request throttled by the venue.
    BadRequest: Malformed request parameters or a rejected order.
    ApiError: Any other error code.
  """
  code = error['code']
  message = error['message']
  data = error.get('data')
  if code in AUTH_CODES:
    raise AuthError(code, message, data)
  if code in RATE_LIMIT_CODES:
    raise RateLimited(code, message, data)
  if code == BAD_REQUEST_CODE or code in TRADING_ERROR_RANGE:
    raise BadRequest(code, message, data)
  raise ApiError(code, message, data)


def unwrap(payload: str | bytes | Any) -> Any:
  """Return the `result` of a JSON-RPC envelope, raising on an `error`.

  Args:
    payload: The raw response body (HTTP) or already-decoded envelope (WebSocket).

  Raises:
    ValidationError: `payload` is not a recognizable JSON-RPC envelope.
    AuthError | RateLimited | BadRequest | ApiError: The envelope carried an `error`.
  """
  envelope = validate_envelope(payload)
  if 'error' in envelope:
    raise_error(envelope['error'])
  return envelope.get('result')
