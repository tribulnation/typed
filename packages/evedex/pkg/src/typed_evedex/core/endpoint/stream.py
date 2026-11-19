"""Base endpoint class for WebSocket channel subscriptions."""

from typing_extensions import (
  Any,
  Literal,
  Mapping,
  Protocol,
  Self,
  TypedDict,
  TypeVar,
  cast,
)
from dataclasses import dataclass
from types import UnionType
import re

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)

Namespace = Literal['exchange', 'market-data']
"""Which Centrifugo namespace a channel lives in: the environment's exchange prefix
(`futures-perp:`, `futures-perp-beta:`) or the shared `market-data:`."""


class StreamClient(Protocol):
  """Structural interface a transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    channel: str,
    *,
    namespace: Namespace = 'exchange',
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a public channel (name without its namespace prefix)."""
    ...

  def authed_subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to one of the account's private channels.

    `channel` is the channel's base name (`order`); the core appends the account's
    `exchangeId` (`order-5055`), resolved on connect.

    Raises:
      AuthError: Lazily, on connect: the client has no wallet key (private channels need a
        JWT session; an API key cannot open them).
    """
    ...

  async def __aenter__(self) -> Self:
    """Take ownership of the transport."""
    ...

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Release the transport."""
    ...


class Meta(TypedDict, total=False):
  """Per-endpoint facts of a channel (`codegen/config.toml`'s `[cores.streams]`)."""

  auth: Literal['private']
  """A private channel of the account: `channel` is its base name, suffixed with the
  account's `exchangeId` on subscribe."""
  namespace: Literal['market-data']
  """The channel lives in the shared `market-data:` namespace, not the exchange one."""


PLACEHOLDER = re.compile(r'\{([^{}]+)\}')
"""A `{name}` slot of a channel template."""


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for stream endpoints."""

  client: StreamClient

  async def __aenter__(self) -> Self:
    """Enter the transport, for use of this endpoint on its own."""
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Exit the transport."""
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    meta: Meta = {},
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to one generated channel.

    Args:
      channel: Channel name without its namespace, `{name}` placeholders filled from
        `parameters`.
      parameters: The generated `Parameters` value, when the channel has any not already
        resolved into `channel`.
      meta: The endpoint's declared quirks.
      validate: Per-call override of message validation.
      request_type: The generated parameters type (unused: Centrifugo subscribes carry no
        parameters beyond the channel name).
      response_type: The generated payload type, which validates each message.
    """
    if isinstance(parameters, Mapping):
      fields = parameters
      channel = PLACEHOLDER.sub(lambda m: str(fields[m.group(1)]), channel)
    message_validator = (
      validator(cast(type[T], response_type)) if response_type is not None else None
    )
    if meta.get('auth') == 'private':
      return self.client.authed_subscribe(
        channel, validator=message_validator, validate=validate
      )
    return self.client.subscribe(
      channel,
      namespace=meta.get('namespace', 'exchange'),
      validator=message_validator,
      validate=validate,
    )
