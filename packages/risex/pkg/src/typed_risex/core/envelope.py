"""The REST envelope and its mapping onto `typed_core` exceptions.

Every successful response is `{"data": <payload>, "request_id": "<uuid>"}`; every failure
is `{"error": {"code": "<gRPC status name>", "message": "..."}, "request_id": "..."}`
with a matching HTTP status. The published OpenAPI documents neither (its error schema is
grpc's `rpcStatus`, with an integer `code`, which the wire never sends). The core returns
`data`, so endpoint schemas describe the payload alone.

On-chain reverts arrive as `FailedPrecondition` with the Solidity error in the message
(`PlaceOrder reverted: SignerNotAuthorized(address) => (0x...)`).
"""

from typing_extensions import Any, NotRequired
import httpx

from typed_core.validation import TypedDict, validator

from .exc import ApiError, AuthError, BadRequest, RateLimited, ValidationError


class ErrorBody(TypedDict):
  """The `error` member of a failed response."""

  code: str
  """gRPC status name: `InvalidArgument`, `Unauthenticated`, `FailedPrecondition`, ..."""
  message: str


class Envelope(TypedDict):
  """A REST response body: `data` on success, `error` on failure."""

  data: NotRequired[Any]
  error: NotRequired[ErrorBody]
  request_id: NotRequired[str]


validate_envelope = validator(Envelope)

AUTH_CODES = frozenset({'Unauthenticated', 'PermissionDenied'})
"""gRPC codes meaning the caller's JWT or signature was rejected or lacks access
(`GET /v1/error-codes`: `E0001`..`E0004`)."""

BAD_REQUEST_CODES = frozenset(
  {
    'InvalidArgument',
    'OutOfRange',
    'FailedPrecondition',
    'NotFound',
    'AlreadyExists',
    'ResourceExhausted',
  }
)
"""gRPC codes meaning the request itself can't succeed as sent. `ResourceExhausted` is
here for its non-throttling uses (`E0210_OrderLimitExceeded`, `E0212_MaxTPSLOrdersReached`,
HTTP 400); throttling is told apart by its HTTP 429."""

AUTH_REVERTS = ('SignerNotAuthorized', 'AllowanceExpired', 'not registered (userId 0)')
"""Revert reasons meaning the signer or allowance isn't authorized for the account, raised
as `AuthError` even though they arrive as `FailedPrecondition`."""

NONCE_REVERTS = ('InvalidNonceAnchor', 'InvalidNonceIndex', 'NonceUsed')
"""Revert reasons meaning the permit's `(anchor, bit)` pair was rejected; the client then
reloads its nonce state before the next signature (see `core.nonces`)."""


def raise_error(status: int, error: ErrorBody, payload: Any):
  """Raise the `typed_core` exception matching one error envelope.

  Args:
    status: HTTP status.
    error: The envelope's `error` member.
    payload: The full response body, attached to the exception.

  Raises:
    RateLimited: HTTP 429.
    AuthError: An authentication/permission code, or a signer/allowance revert.
    BadRequest: Any other caller-side code.
    ApiError: A server-side code (`Internal`, `Unavailable`, ...).
  """
  code, message = error['code'], error['message']
  if status == 429:
    raise RateLimited(code, message, payload)
  if code in AUTH_CODES or any(reason in message for reason in AUTH_REVERTS):
    raise AuthError(code, message, payload)
  if code in BAD_REQUEST_CODES:
    raise BadRequest(code, message, payload)
  raise ApiError(code, message, payload)


def raise_status(response: httpx.Response):
  """Raise for an unsuccessful response that carries no error envelope (Cloudflare, say).

  Raises:
    AuthError: Status `401`/`403`.
    RateLimited: Status `429`.
    BadRequest: Any other `4xx`.
    ApiError: Any other status.
  """
  status, text = response.status_code, response.text
  if status in (401, 403):
    raise AuthError(status, text)
  if status == 429:
    raise RateLimited(status, text)
  if 400 <= status < 500:
    raise BadRequest(status, text)
  raise ApiError(status, text)


def unwrap(response: httpx.Response) -> Any:
  """Return a response's `data`, raising the mapped exception on failure.

  Raises:
    ValidationError: A successful response that is not a recognizable envelope.
    ApiError: The response carried an error (see `raise_error`/`raise_status`).
  """
  try:
    envelope = validate_envelope(response.content)
  except ValidationError:
    if not response.is_success:
      raise_status(response)
    raise
  if (error := envelope.get('error')) is not None:
    raise_error(response.status_code, error, envelope)
  if not response.is_success:
    raise_status(response)
  # A missing `data` is left to the endpoint's own response validation: never raise on a
  # successful write just because its payload was empty.
  return envelope.get('data')
