"""Spot's request/response mixins: the base classes every hand-written and generated
spot endpoint class inherits.

`BaseMixin.output()` is the one place a decoded HTTP response becomes either a
validated return value or a raised exception, for every spot endpoint method. It routes
through `..envelope.unwrap()` -- the same mapping `spot/streams/core/auth.py`'s
listen-key bootstrap already uses -- so a failing response raises the `typed_core`
exception spot's own error-code table documents (`AuthError`/`RateLimited`/`BadRequest`/
`ApiError`), not a code-blind `ApiError` regardless of cause
(docs/production_standards.md S9).
"""

from typing_extensions import TypedDict, TypeVar
from dataclasses import dataclass, field
import httpx

from typed_mexc.core import HttpMixin, ValidationMixin, validator
from .auth import AuthHttpMixin
from .envelope import unwrap

T = TypeVar('T')

MEXC_SPOT_API_BASE = 'https://api.mexc.com'


class ErrorResponse(TypedDict):
  """Spot's error shape. Folded into every generated response type's validator union
  (`X | ErrorResponse`) purely so `output()`'s generic `T` resolves to the real success
  type `X` -- see `output()` below. `unwrap()` always raises before an error payload
  reaches validation, so this member is never actually matched at runtime.
  """

  msg: str
  code: int


class BaseMixin(ValidationMixin):
  """Shared response handling for every spot endpoint mixin (`SpotMixin`/`AuthSpotMixin`)."""

  def output(self, response: httpx.Response, validator: validator[T | ErrorResponse], validate: bool | None) -> T:
    """Unwrap a spot HTTP response and optionally validate the successful payload.

    `validator`'s declared type is `T | ErrorResponse`, not just `T`: pattern-matching
    that union against a generated `adapter = validator(SomeResponse | ErrorResponse)`
    is what lets `output()`'s own return type resolve to the real success type `T`
    rather than the whole union -- a type-level trick only, since `unwrap()` already
    raises on any error response before this method ever calls `validator.python(...)`.

    Args:
      response: The raw HTTP response.
      validator: Validates the decoded payload when validation is enabled.
      validate: Per-call validation override; `None` defers to `self.default_validate`.

    Raises:
      AuthError: Key, signature or permission rejection (`envelope.unwrap`).
      RateLimited: Request throttled.
      BadRequest: Any other `4xx` status.
      ApiError: Any other non-zero embedded `code`, or unsuccessful non-4xx status.
      ValidationError: The body was not JSON, or failed validation.
    """
    payload = unwrap(response)
    obj = validator.python(payload) if self.validate(validate) else payload
    return obj  # type: ignore


@dataclass
class SpotMixin(HttpMixin, BaseMixin):
  """Public (unauthenticated) spot HTTP endpoint mixin."""

  base_url: str = field(default=MEXC_SPOT_API_BASE, kw_only=True)


@dataclass
class AuthSpotMixin(AuthHttpMixin, BaseMixin):
  """Authenticated (signed) spot HTTP endpoint mixin."""

  base_url: str = field(default=MEXC_SPOT_API_BASE, kw_only=True)
