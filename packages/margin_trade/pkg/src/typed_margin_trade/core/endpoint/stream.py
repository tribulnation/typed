"""Base endpoint class for WebSocket channels (`client.streams`): one `subscribe()` call per
channel method.

There is no WebSocket authentication: user channels take an address, like `/info`.
"""

from typing_extensions import (
  Any,
  Mapping,
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
R = TypeVar('R', default=Any)


class StreamMeta(TypedDict):
  """Per-channel quirks of a WebSocket subscription."""

  channel: NotRequired[str]
  """The `channel` tag pushes arrive under, when it differs from the subscription `type`."""
  route: NotRequired[dict[str, str]]
  """How to tell concurrent subscriptions to one channel apart: each subscription field
  that identifies a stream (`coin`), mapped to where each push carries it (`coin`,
  `[0].coin` for a list of trades, `s` for a candle). Absent: one subscription per channel.
  """


class StreamClient(Protocol):
  """Structural interface the WebSocket transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    subscription: Mapping[str, Any],
    *,
    channel: str | None = None,
    route: Mapping[str, str] | None = None,
    validator: 'validator[T] | None' = None,
    reply_validator: 'validator[R] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, R, Any]':
    """Subscribe with `subscription` (`type` plus parameters), validating each push.

    Args:
      subscription: The `subscription` object sent on the wire.
      channel: Push tag, when it differs from `subscription['type']`.
      route: See `StreamMeta.route`.
      validator: Validator for each push's `data`.
      reply_validator: Validator for the subscribe acknowledgement's `data`.
      validate: Per-call override of push and acknowledgement validation.
    """
    ...

  async def __aenter__(self) -> Self:
    """Take ownership of the connection (connecting lazily, on the first subscription)."""
    ...

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Close the connection, if it was opened."""
    ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for WebSocket channel endpoints."""

  client: StreamClient
  """The WebSocket transport."""

  async def __aenter__(self) -> Self:
    """Return this surface; the WebSocket opens lazily, on the first subscription.

    Opens and closes nothing: only the root client closes the shared connection.
    """
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Do nothing: only the root client closes the shared connection."""

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    meta: StreamMeta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
    reply_type: type[R] | UnionType | None = None,
  ) -> 'StreamManager[T, R, Any]':
    """Subscribe to one channel: `{"type": channel, **parameters}` goes out as the
    `subscription`, each push's `data` comes back validated.

    Args:
      channel: Subscription `type` (`l2Book`, `orderUpdates`, ...).
      parameters: The channel's `Parameters` value, or `None` for a parameterless channel.
      meta: This channel's quirks: its push tag and how its pushes are routed.
      validate: Per-call override of push validation.
      request_type: The channel's parameters type, used to serialize `parameters`.
      response_type: The channel's payload type, used to validate each push.
      reply_type: The subscribe acknowledgement's type, used to validate it.
    """
    subscription = {'type': channel, **dump_request(parameters, request_type)}
    payload_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    reply_validator = validator(reply_type) if reply_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(
      subscription,
      channel=meta.get('channel'),
      route=meta.get('route'),
      validator=payload_validator,
      reply_validator=reply_validator,
      validate=validate,
    )
