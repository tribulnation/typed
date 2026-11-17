"""Base endpoint class for the WebSocket feed: one `subscribe()` call per stream method."""

from typing_extensions import (
  Any,
  Literal,
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

StreamAuth = Literal['required', 'optional']
"""How a channel relates to the connection's `auth_v2` handshake."""


class StreamMeta(TypedDict):
  """Per-channel quirks of a WebSocket subscription. `{}` is a public channel."""

  auth: NotRequired[StreamAuth]
  """`required` for a channel only an authenticated connection may join (`fills`,
  `account`); `optional` for one that authentication pins to the client's own account
  (`orders`, `positions`, `funding`: authenticated when the client has a signer key, the
  venue-wide feed otherwise)."""


class StreamClient(Protocol):
  """Structural interface the WebSocket transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    auth: StreamAuth | None = None,
    validator: 'validator[T] | None' = None,
    reply_validator: 'validator[R] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, R, Any]':
    """Subscribe to `channel` with `params` as its filter (`market_ids`, `makers`),
    authenticating the connection first per `auth`, validating each push through
    `validator` and the subscribe acknowledgement through `reply_validator`.
    """
    ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for WebSocket channel endpoints."""

  client: StreamClient
  """The WebSocket transport."""

  async def __aenter__(self) -> Self:
    """Return this surface; the connection opens on the first subscription."""
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
    """Subscribe to one channel.

    Args:
      channel: Channel name, e.g. `orderbook`.
      parameters: The channel's `Parameters` value (its filter), or `None` for no filter.
      meta: This channel's quirks: whether it needs an authenticated connection.
      validate: Per-call override of pushed-message validation.
      request_type: The channel's parameters type, used to serialize `parameters`.
      response_type: The channel's message type, used to validate each push.
      reply_type: The subscribe acknowledgement's type (`Stream.reply`), used to validate it.
    """
    values = dump_request(parameters, request_type)
    message_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    reply_validator = validator(reply_type) if reply_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(
      channel,
      values or None,
      auth=meta.get('auth'),
      validator=message_validator,
      reply_validator=reply_validator,
      validate=validate,
    )
