"""Nado's response envelopes and their mapping onto `typed_core` exceptions.

Two shapes, both answering API errors with HTTP `200` as often as not:

- engine (gateway queries, edge queries and executes, and the trigger service):
  `{status: "success"|"failure", data?, error?, error_code?, request_type, signature?}`.
  Success unwraps to `data`. Edge `ping`/`time` carry no `data`
  (`{status, method, id, server_time}`), so they return the frame itself.
- bare (archive, rewards, and both REST v2 APIs): the payload itself on success,
  `{error, error_code}` on failure (HTTP `400` on the REST APIs).

A request the server cannot even parse is answered with a plain-text HTTP `422` (HTTP) or a
plain-text frame (gateway WebSocket), and a missing `Accept-Encoding` with HTTP `403`.
"""

from typing_extensions import Any, Literal, NoReturn, NotRequired
import json

import httpx

from typed_core.validation import TypedDict

from .exc import ApiError, AuthError, BadRequest, RateLimited, ValidationError

RATE_LIMIT_CODES = frozenset({1000, 1015})
"""`RateLimit`: request weight over the per-IP or per-wallet budget."""

AUTH_CODES = frozenset({1001, 1002, 1003, 2014, 2027, 2028, 2029, 2034, 2035, 2050})
"""Codes rejecting who is asking rather than what: a blacklisted address or blocked
location (1001-1003), a cancel for another subaccount (2014), and every signature failure
(2027 length, 2028 signer is neither the sender nor its linked signer, 2029 zero signer,
2034 bad `v`, 2035 other signature error, 2050 unauthorized action)."""

API_CODES = frozenset({1004, 2053, 2063, 2068, 4003, 5000})
"""Codes reporting a venue-side fault rather than a bad request: maintenance (1004, 2068),
an internal matching or query error (2053, 2063, 5000) and an EVM revert (4003)."""


class EngineEnvelope(TypedDict):
  """Every engine response (gateway queries and executes, edge queries, trigger)."""

  status: Literal['success', 'failure']
  data: NotRequired[Any]
  error: NotRequired[str]
  error_code: NotRequired[int]
  request_type: NotRequired[str]


def raise_code(code: int | None, message: str, payload: Any) -> NoReturn:
  """Raise the `typed_core` exception matching a Nado error code.

  Codes are from the docs' error table: 1xxx general, 2xxx execute and query, 3xxx
  indexer, 4xxx other, 5000 internal. Every 2xxx/3xxx code not listed as an auth or venue
  fault describes a request the venue refused as asked (invalid price increment, unhealthy
  order, post-only crossing the book, ...), so it is a `BadRequest`.

  Args:
    code: The venue's `error_code`, if any.
    message: The venue's `error` message.
    payload: The whole response, attached for debugging.

  Raises:
    RateLimited: 1000/1015, or a code-less `rate limited` message.
    AuthError: An `AUTH_CODES` code.
    ApiError: An `API_CODES` code, a 4xxx code other than 4000, or no code at all.
    BadRequest: Any other code.
  """
  if code in RATE_LIMIT_CODES or (code is None and 'rate limit' in message.lower()):
    raise RateLimited(code, message, payload)
  if code is None:
    raise ApiError(None, message, payload)
  if code in AUTH_CODES:
    raise AuthError(code, message, payload)
  if code in API_CODES or 4000 < code < 5000:
    raise ApiError(code, message, payload)
  raise BadRequest(code, message, payload)


def decode(text: str | bytes) -> Any:
  """Decode a JSON body, or `None` when it is not JSON (a plain-text rejection)."""
  try:
    return json.loads(text)
  except ValueError:
    return None


def unwrap_engine(payload: Any, *, frame: bool = False, echo_id: bool = False) -> Any:
  """The result of one decoded engine response: `data`, or the whole frame when `frame`.

  Args:
    payload: The decoded response.
    frame: Return the success frame itself (edge `ping`/`time`, which carry no `data`).
    echo_id: Keep the request `id` an execute's envelope echoes beside `data`: copied into
      `data` when `data` is an object without its own `id`.

  Raises:
    ValidationError: The response is not an engine envelope.
    ApiError: `status` is `failure` (see `raise_code` for the subclass).
  """
  if not isinstance(payload, dict) or payload.get('status') not in (
    'success',
    'failure',
  ):
    if (
      isinstance(payload, dict) and 'error' in payload
    ):  # an HTTP 400 `{error, error_code}`
      code = payload.get('error_code')
      raise_code(
        code if isinstance(code, int) else None, str(payload['error']), payload
      )
    raise ValidationError(f'Not a Nado engine envelope: {payload!r:.500}')
  if payload['status'] == 'failure':
    code = payload.get('error_code')
    raise_code(
      code if isinstance(code, int) else None, str(payload.get('error', '')), payload
    )
  if frame:
    return payload
  data = payload.get('data')
  if (
    echo_id
    and payload.get('id') is not None
    and isinstance(data, dict)
    and 'id' not in data
  ):
    return {**data, 'id': payload['id']}
  return data


def unwrap_bare(payload: Any) -> Any:
  """The result of one decoded archive, rewards or REST v2 response.

  Raises:
    ApiError: The body is an `{error, error_code}` object (see `raise_code`).
  """
  if (
    isinstance(payload, dict)
    and 'error' in payload
    and ('error_code' in payload or len(payload) == 1)
  ):
    code = payload.get('error_code')
    raise_code(code if isinstance(code, int) else None, str(payload['error']), payload)
  return payload


def check_http(response: httpx.Response) -> Any:
  """Decode an HTTP response, raising on a status that carries no usable body.

  A non-2xx JSON body naming an error (an `error` key: `{error, error_code}`, HTTP `400` on
  the REST APIs; or an engine envelope with `status: "failure"`) is returned for the envelope
  check to map, since its code is more precise than the status. Any other non-2xx body (a
  proxy's `{"status": 503}`, say) is mapped by the HTTP status alone, never returned as data.

  Raises:
    AuthError: HTTP `401`/`403` (including a missing `Accept-Encoding`).
    RateLimited: HTTP `429`.
    BadRequest: Any other `4xx` without an error body (a plain-text `422`: the body did not
      parse as a request).
    ApiError: A `5xx`.
    ValidationError: A `2xx` body that is not JSON.
  """
  payload = decode(response.content)
  if response.is_success:
    if payload is None and response.content.strip() != b'null':
      raise ValidationError(f'Response is not JSON: {response.text[:500]!r}')
    return payload
  if isinstance(payload, dict) and (
    'error' in payload or payload.get('status') == 'failure'
  ):
    return payload
  status = response.status_code
  body = payload if payload is not None else response.text
  if status in (401, 403):
    raise AuthError(status, body)
  if status == 429:
    raise RateLimited(status, body)
  if 400 <= status < 500:
    raise BadRequest(status, body)
  raise ApiError(status, body)
