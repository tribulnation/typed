"""Futures' request/response mixins: the base classes every hand-written and generated
futures endpoint class inherits.

`BaseMixin.envelope_output()` is the one place a decoded HTTP response becomes either a
validated return value or a raised exception, for every futures endpoint method. It
routes through `..envelope.unwrap()`, so a failing response raises the `typed_core`
exception futures' own error-code table documents (`AuthError`/`RateLimited`/
`BadRequest`/`ApiError`), not a code-blind `ApiError` regardless of cause
(docs/production_standards.md S9).
"""

from typing_extensions import TypeVar, Any
from dataclasses import dataclass, field
import httpx

from typed_mexc.core import HttpMixin, ValidationMixin, validator
from .auth import AuthHttpMixin
from .envelope import unwrap

T = TypeVar('T', default=Any)

MEXC_FUTURES_API_BASE = 'https://contract.mexc.com'


class BaseMixin(ValidationMixin):
  """Shared response handling for every futures endpoint mixin (`FuturesMixin`/`AuthFuturesMixin`)."""

  def envelope_output(self, response: httpx.Response, validator: validator[T], validate: bool | None) -> T:
    """Unwrap a futures HTTP response and optionally validate the whole envelope.

    Futures keeps the whole envelope rather than stripping to `data` (see `envelope.py`),
    so `validator` is expected to validate against the endpoint's own full-envelope
    `TypedDict`, not just its `data` payload.

    Args:
      response: The raw HTTP response.
      validator: Validates the decoded envelope when validation is enabled.
      validate: Per-call validation override; `None` defers to `self.default_validate`.

    Raises:
      AuthError: Key, signature or permission rejection (`envelope.unwrap`).
      RateLimited: Request throttled, or request time outside the accepted window.
      BadRequest: Any other `4xx` status.
      ApiError: Any other non-zero embedded `code`, `success: false`, or unsuccessful
        non-4xx status.
      ValidationError: The body was not JSON, not a recognizable envelope, or failed
        validation.
    """
    envelope = unwrap(response)
    return validator.python(envelope) if self.validate(validate) else envelope  # type: ignore


@dataclass
class FuturesMixin(HttpMixin, BaseMixin):
  """Public (unauthenticated) futures HTTP endpoint mixin."""

  base_url: str = field(default=MEXC_FUTURES_API_BASE, kw_only=True)


@dataclass
class AuthFuturesMixin(AuthHttpMixin, BaseMixin):
  """Authenticated (signed) futures HTTP endpoint mixin."""

  base_url: str = field(default=MEXC_FUTURES_API_BASE, kw_only=True)
