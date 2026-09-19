"""Keep path credentials out of request diagnostics without changing wire URLs."""

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
import logging
from typing_extensions import Any, Iterator
from urllib.parse import quote, unquote, urlsplit

import httpx

from .exc import Error, NetworkError, REDACTED


@dataclass(frozen=True)
class Redactor:
  """The configured key and the credential embedded in one surface's base URL."""

  secrets: tuple[str, ...] = field(repr=False)

  @classmethod
  def new(cls, *, api_key: str, base_url: str) -> 'Redactor':
    """Include encoded and decoded spellings of both credentials, longest first."""
    # A base URL ends at the credential; REST operation paths are added later.
    embedded = urlsplit(base_url).path.rstrip('/').rsplit('/', 1)[-1]
    values = {api_key, embedded, unquote(embedded)} - {''}
    values.update(quote(value, safe='') for value in tuple(values))
    return cls(tuple(sorted(values, key=len, reverse=True)))

  def text(self, value: str) -> str:
    """Replace credentials in rendered diagnostics."""
    for secret in self.secrets:
      value = value.replace(secret, REDACTED)
    return value

  def value(self, value: Any) -> Any:
    """Preserve structured API error arguments while removing echoed credentials."""
    if isinstance(value, str):
      return self.text(value)
    if isinstance(value, bytes):
      for secret in self.secrets:
        value = value.replace(secret.encode(), REDACTED.encode())
      return value
    if isinstance(value, dict):
      return {self.value(key): self.value(item) for key, item in value.items()}
    if isinstance(value, list):
      return [self.value(item) for item in value]
    if isinstance(value, tuple):
      return tuple(self.value(item) for item in value)
    return value


_active: ContextVar[Redactor | None] = ContextVar(
  'alchemy_request_redactor', default=None
)


class RequestLogFilter(logging.Filter):
  """Sanitize transport records before handlers, only during an Alchemy request."""

  def filter(self, record: logging.LogRecord) -> bool:
    """Materialize safe text, including exception text, before a handler queues it."""
    redactor = _active.get()
    if redactor is not None:
      record.msg = redactor.text(record.getMessage())
      record.args = ()
      if record.exc_info:
        record.exc_text = redactor.text(
          logging.Formatter().formatException(record.exc_info)
        )
        record.exc_info = None
      elif record.exc_text:
        record.exc_text = redactor.text(record.exc_text)
      if record.stack_info:
        record.stack_info = redactor.text(record.stack_info)
    return True


_log_filter = RequestLogFilter()
# Logger filters do not run on propagated child records: attach to each transport
# emitter, including HTTP/2 and SOCKS emitters which httpcore imports lazily.
_TRANSPORT_LOGGERS = (
  'httpx',
  'httpcore.connection',
  'httpcore.http11',
  'httpcore.http2',
  'httpcore.proxy',
  'httpcore.socks',
)


@contextmanager
def protect_request(*, api_key: str, base_url: str) -> Iterator[None]:
  """Protect transport logs and raised errors for one request, including validation.

  Context variables isolate concurrent calls. Filters retain no credentials and leave
  unrelated logging untouched. Original exceptions are suppressed because their causes
  may hold unredacted URLs or response bodies.
  """
  redactor = Redactor.new(api_key=api_key, base_url=base_url)
  for name in _TRANSPORT_LOGGERS:
    logging.getLogger(name).addFilter(_log_filter)
  token = _active.set(redactor)
  try:
    yield
  except Error as error:
    raise type(error)(*redactor.value(error.args)) from None
  except (httpx.HTTPError, httpx.InvalidURL) as error:
    raise NetworkError(redactor.text(str(error))) from None
  except ValueError as error:
    raise ValueError(redactor.text(str(error))) from None
  finally:
    _active.reset(token)
