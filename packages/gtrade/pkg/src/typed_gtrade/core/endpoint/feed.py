"""Base endpoint class for the push-only feeds: the per-chain backend's event stream and
the pricing stream. Neither has a subscribe protocol or authentication: the server pushes
everything from the moment the connection opens, and each endpoint picks its frames out
by a local channel name."""

from typing_extensions import Any, Protocol, Self, TypeVar
from dataclasses import dataclass
from types import UnionType

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class FeedClient(Protocol):
  """Structural interface a push-only feed transport implements."""

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Deliver the frames the transport routes to `channel`, validating each against
    `validator` if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class FeedEndpoint:
  """Base class for push-only feed endpoints."""

  client: FeedClient

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
    """Receive one kind of frame from the feed.

    Args:
      channel: The local channel: a backend event name (`currentBlock`, `liveEvent`,
        ...), or `prices`/`heartbeat` on the pricing stream.
      parameters: Unused: a feed takes no subscription parameters.
      validate: Per-call override of frame validation.
      request_type: Unused, as `parameters`.
      response_type: The generated payload type, used to validate each frame.
    """
    frame_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(channel, validator=frame_validator, validate=validate)
