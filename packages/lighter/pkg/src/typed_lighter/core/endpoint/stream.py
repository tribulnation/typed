"""Base endpoint class for WebSocket channels (`client.streams`): one `subscribe()` call per channel method."""

from typing_extensions import (
  Any,
  Literal,
  NotRequired,
  Protocol,
  Self,
  TypedDict,
  TypeVar,
)
from dataclasses import dataclass
from types import UnionType

from typed_core.util import StreamManager
from typed_core.validation import validator

from .wire import dump_request

T = TypeVar('T', default=Any)


class StreamMeta(TypedDict):
  """Per-channel quirks of a WebSocket subscription."""

  auth: NotRequired[Literal['token']]
  """`token` when the channel needs an auth token in its subscribe frame; absent when public."""


class StreamClient(Protocol):
  """Structural interface the WebSocket transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    channel: str,
    *,
    authed: bool = False,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to `channel` (slash form, e.g. `order_book/0`), attaching a token when `authed`."""
    ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for WebSocket channel endpoints."""

  client: StreamClient
  """The WebSocket transport."""

  async def __aenter__(self) -> Self:
    """Return this surface; the WebSocket transport opens lazily, on first use.

    Entering or leaving it with `async with` opens and closes nothing: the transport is shared
    with sibling surfaces, and only the root client (`core.client.ClientBase`) closes it.
    """
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client closes the WebSocket transport, which sibling surfaces
    may still be using."""

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    meta: StreamMeta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to one channel: fill `channel`'s `{placeholders}` from `parameters`, then
    subscribe, with a token when `meta['auth']` says so.

    Args:
      channel: Channel template, e.g. `order_book/{market_id}`.
      parameters: The channel's `Parameters` value, or `None` for a fixed channel.
      meta: This channel's quirks: whether it needs a token.
      validate: Per-call override of pushed-payload validation.
      request_type: The channel's parameters type, used to serialize `parameters`.
      response_type: The channel's payload type, used to validate each push.
    """
    values = dump_request(parameters, request_type)
    resolved = channel.format(**values) if values else channel
    payload_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(
      resolved,
      authed=meta.get('auth') == 'token',
      validator=payload_validator,
      validate=validate,
    )
