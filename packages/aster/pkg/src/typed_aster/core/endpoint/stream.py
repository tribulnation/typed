"""Base endpoint class for public market-data streams (`<symbol>@bookTicker`, ...), served
on the combined-stream connection of each surface. Every market stream is public, so
there is no `meta`."""

from typing_extensions import Any, Protocol, Self, TypeVar
from dataclasses import dataclass
from types import UnionType

from typed_core.util import StreamManager
from typed_core.validation import validator

from .wire import dump_request

T = TypeVar('T', default=Any)


class StreamClient(Protocol):
  """Structural interface a transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to one stream, validating each push against `validator` if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for market-data stream endpoints."""

  client: StreamClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to one stream, filling `channel`'s `{placeholder}`s from `parameters`.

    Args:
      channel: The stream name or template, e.g. `{symbol}@bookTicker`. Aster expects
        symbols lowercase in stream names.
      parameters: The generated value filling the placeholders, or `None`.
      validate: Per-call override of push validation.
      request_type: The generated parameters type, used to serialize `parameters`.
      response_type: The generated payload type, used to validate each push.
    """
    values = dump_request(parameters, request_type) or {}
    resolved = channel.format(**values) if values else channel
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(
      resolved, validator=response_validator, validate=validate
    )
