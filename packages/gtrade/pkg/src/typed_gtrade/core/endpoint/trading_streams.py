"""Base endpoint class for the Trading API WebSocket channels: one `subscribe()` call per
endpoint method, whose `meta` says whether the channel is private."""

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


class StreamMeta(TypedDict):
  """Per-channel facts of a Trading API subscription. `{}` is a public channel."""

  auth: NotRequired[Literal['read']]
  """`read` for a private channel (`orders`, `fills`, `positions`, `account`): the
  connection authenticates once, with the API key or the agent signature, before its
  first private subscription."""


class TradingStreamClient(Protocol):
  """Structural interface the Trading API's WebSocket transport implements."""

  def subscribe(
    self,
    channel: str,
    keys: Mapping[str, Any] | None = None,
    *,
    private: bool = False,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to one channel, validating each data frame against `validator` if given.

    Args:
      channel: The channel name (`book`, `orders`, ...).
      keys: The channel's keys (`market`, `interval`), sent in the subscribe frame.
      private: Authenticate the connection first.
      validator: Data frame validator.
      validate: Per-call override of validation.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class TradingStreamEndpoint:
  """Base class for Trading API WebSocket channel endpoints."""

  client: TradingStreamClient

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
    meta: StreamMeta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to one channel. Each item is the whole data frame (`channel`, its keys,
    `snapshot`, `seq` where the channel numbers frames, and `data`): the first is the
    snapshot, and a `seq` gap means resubscribing for a fresh one.

    Args:
      channel: The channel name.
      parameters: The generated value carrying the channel's keys, or `None`.
      meta: Whether the channel is private.
      validate: Per-call override of frame validation.
      request_type: The generated parameters type, used to serialize `parameters`.
      response_type: The generated frame type, used to validate each frame.
    """
    keys = dump_request(parameters, request_type)
    frame_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(
      channel,
      keys,
      private=meta.get('auth') == 'read',
      validator=frame_validator,
      validate=validate,
    )
