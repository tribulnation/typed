"""Kraken Futures public REST transport and logical error handling."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.validation import validator

from ..core.transport.public import PublicHttpClient


class FuturesEnvelope(TypedDict):
  """Result marker and error fields shared by Futures REST responses."""

  result: Literal['success', 'error']
  error: NotRequired[str]
  errors: NotRequired[list[str]]


validate_envelope = validator(FuturesEnvelope)


class FuturesHttpClient(PublicHttpClient):
  """Keep native response fields and reject Futures logical errors."""

  def payload(self, response: httpx.Response) -> Any:
    """Check the Futures result marker independently of endpoint validation."""
    payload = super().payload(response)
    envelope = validate_envelope.python(payload)
    if envelope['result'] == 'error':
      message = envelope.get('error', '')
      if message == 'apiLimitExceeded':
        raise RateLimited(message)
      if message in {
        'authenticationError',
        'accountInactive',
        'apiKeyExpired',
        'apiKeyRevoked',
      }:
        raise AuthError(message)
      if message in {'invalidArgument', 'invalidSymbol', 'requiredArgumentMissing'}:
        raise BadRequest(message)
      raise ApiError(message, envelope.get('errors'))
    return payload
