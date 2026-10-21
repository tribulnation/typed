"""Margin Trade's response envelopes and their mapping onto `typed_core` exceptions.

Every HTTP route shares one error model with three layers, all of which have to be checked:

1. A non-2xx status with `{"error": "<msg>"}` (malformed body, unsupported `/exchange` or
   `/solana` action, unknown announcement or ticker), or with an empty body (`/solana`
   answers an unparseable envelope that way). A non-2xx body is decoded as JSON whenever it
   parses, whatever its content type; one that does not (a bare-text 429, an HTML 502 from a
   proxy) is mapped by status, with its text as the message.
2. A 200 soft error disguised as success:
   `{"status": "ok", "response": {"type": "<t>", "data": {"status": {"error": "<msg>"}}}}`
   (unknown type, missing parameter, signature refused, wrong network code, ...).
3. A 200 `{"status": "err", "response": "<msg>"}`: `/exchange` business rejections, per the
   docs (not observed yet).

A successful `/exchange` call is wrapped `{"status": "ok", "response": {"type", "data"}}`
and is unwrapped to `data`; an action with no result answers `{"status": "ok", "response":
"default"}` and is unwrapped to `None` (the `"default"` placeholder carries nothing). Every
other success is bare JSON and returned as is. Only a body carrying both `status` (`ok`/`err`)
and `response` is an envelope: `/info orderStatus` answers a bare `{"status": "order" | "not
found", ...}` that must pass through untouched.
Per-order failures inside `statuses` are results, not errors, and are never raised.
"""

from typing_extensions import Any, Literal, TypeGuard

import httpx

from typed_core.exceptions import (
  ApiError,
  AuthError,
  BadRequest,
  RateLimited,
  ValidationError,
)


AUTH_MESSAGES = (
  'authentication required',
  'signature verification failed',
  'duplicate signature',
  'is not operable by this signer',
  'timestamp too far from server time',
)
"""Lower-cased fragments of the error messages meaning the signature, signer or its clock
was refused, each matching one message observed on testnet: `Authentication required: use
signed request format`, `signature verification failed`, `duplicate signature`, `declared
account <a> is not operable by this signer`, `timestamp too far from server time: ...`.

Whole phrases, not a bare `signature`: a parameter error naming a field such as
`agentConsentSignature` is a `BadRequest`, not an auth failure. The venue publishes no error
codes, so messages are all there is to go on.
"""


def decode(response: httpx.Response) -> Any:
  """Decode a JSON body; a non-JSON body (`/health`) comes back as text.

  Raises:
    ValidationError: The body claims to be JSON but is not.
  """
  if 'json' not in response.headers.get('content-type', 'application/json'):
    return response.text
  try:
    return response.json()
  except ValueError as e:
    raise ValidationError(f'Response is not valid JSON: {response.text[:200]!r}') from e


def decode_error(response: httpx.Response) -> Any:
  """Decode a non-2xx body: JSON whenever it parses, whatever its content type (a JSON
  `{"error"}` sent as `text/plain` still yields its message), its text otherwise; `None` when
  empty. Never raises.
  """
  if response.content:
    try:
      return response.json()
    except ValueError:
      return response.text


def is_auth_message(message: str) -> bool:
  """Whether an error message means the signature, signer or account was refused."""
  lowered = message.lower()
  return any(fragment in lowered for fragment in AUTH_MESSAGES)


def raise_message(message: str, payload: Any, *, status: int | None = None):
  """Raise the `typed_core` exception matching one error message.

  Args:
    message: The venue's error message.
    payload: The full body, attached for debugging.
    status: The HTTP status, when the error came with a non-2xx one.

  Every exception carries `(message, payload)`, plus `status` when there is one.

  Raises:
    AuthError: The message, or a 401/403 status, means the signature or signer was refused.
    RateLimited: Status 429.
    BadRequest: Any other 4xx status, or a soft error (the request itself was refused).
    ApiError: Any other unsuccessful status, or an `/exchange` business rejection.
  """
  args = (message, payload) if status is None else (message, payload, status)
  if status in (401, 403) or is_auth_message(message):
    raise AuthError(*args)
  elif status == 429:
    raise RateLimited(*args)
  elif status is None or 400 <= status < 500:
    raise BadRequest(*args)
  else:
    raise ApiError(*args)


def error_message(payload: Any) -> str | None:
  """The message of a soft error (`data.status.error` inside an ok envelope), if `payload`
  is one.
  """
  if isinstance(data := payload, dict) and isinstance(
    status := data.get('status'), dict
  ):
    error = status.get('error')
    if isinstance(error, str):
      return error


def is_envelope(payload: Any) -> TypeGuard[dict[str, Any]]:
  """Whether `payload` is the `{status: ok|err, response}` wrapper, not a bare result that
  happens to carry a `status` field.
  """
  return (
    isinstance(payload, dict)
    and payload.get('status') in ('ok', 'err')
    and 'response' in payload
  )


def unwrap(response: httpx.Response) -> Any:
  """The result of one HTTP call, raising on any of the three error layers.

  Raises:
    ValidationError: A successful response's body was not valid JSON.
    AuthError: The signature or signer was refused.
    RateLimited: Status 429.
    BadRequest: The request was refused (non-2xx `{"error"}`, or a soft error).
    ApiError: An `/exchange` business rejection, or any other failure.
  """
  if not response.is_success:
    payload = decode_error(response)
    message = payload.get('error') if isinstance(payload, dict) else payload
    raise_message(
      str(message or response.reason_phrase)[:500], payload, status=response.status_code
    )
  payload = decode(response) if response.content else None
  if is_envelope(payload):
    status: Literal['ok', 'err'] = payload['status']
    inner = payload['response']
    if status == 'err':
      message = str(inner)
      raise (AuthError if is_auth_message(message) else ApiError)(message, payload)
    elif isinstance(inner, dict):
      data = inner.get('data')
      if (message := error_message(data)) is not None:
        raise_message(message, payload)
      return data
    elif inner != 'default':
      return inner
  else:
    return payload
