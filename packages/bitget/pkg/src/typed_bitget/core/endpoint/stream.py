"""Base endpoint class for Classic/Uta WebSocket stream endpoints: design §2/§8's single
`subscribe()` verb, deciding public-vs-private purely from `meta['private']`. Also
exposes `authed_command`, unrelated to design §2/§8 -- an id-correlated WS trade command
(`place-order`/`cancel-order`, Classic only today) is structurally different from every
generated subscription (its `id` is connection-managed, not a caller-facing request
field), so it is never called from generated code, only from the two hand-written
leaves that need it (`classic_streams/order/place.py`, `.../cancel.py`).
"""

from typing_extensions import Any, Mapping, NotRequired, Protocol, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json as _json

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class Meta(TypedDict):
  """`classic_streams`/`uta_streams`'s own `meta` shape (`codegen/config.toml`
  `[cores.classic_streams]`/`[cores.uta_streams]`): whether this channel is private
  (needs a logged-in connection). Hand-written to match that declared JSON Schema --
  never code-generated (design §2/§6; S27)."""

  private: NotRequired[bool]
  """Whether this channel needs the private, logged-in connection (absent/`False` for a
  public channel)."""


class StreamClient(Protocol):
  """Structural interface a transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    channel: str,
    params: 'Mapping[str, Any] | None' = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a public channel, validating each notification against `validator` if given."""
    ...

  def authed_subscribe(
    self,
    channel: str,
    params: 'Mapping[str, Any] | None' = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a private channel, validating each notification against `validator` if given.

    Raises:
      AuthError: This transport was built with no credentials. Raised lazily, once the
        returned `StreamManager` is actually connected (the login handshake it triggers is
        itself lazy, on first private subscribe on this connection).
    """
    ...

  async def authed_command(
    self,
    req: 'Mapping[str, Any]',
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Send one id-correlated trade command (`place-order`/`cancel-order`) and return its
    reply, validating it against `validator` if given.

    Raises:
      AuthError: This transport was built with no credentials.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for every Classic/Uta WebSocket stream endpoint -- the resolved
  `classic_streams`/`uta_streams` core (`codegen/config.toml`)."""

  client: StreamClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    request: Any = None,
    *,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """One channel subscription (design §2/§8's `subscribe` verb) -- routed to the
    public or private connection purely from `meta['private']`; `channel`'s own
    `{placeholder}` interpolation is entirely the transport's own concern (design §8:
    "the same placeholder-substitution rule as `path`... no per-parameter wire-placement
    logic runs here").

    Args:
      channel: The wire channel template, e.g. `candle{interval}`.
      request: The generated `Parameters` value (a `TypedDict` instance, or `None`).
      meta: This call's own quirks -- whether the channel is private.
      validate: Per-call override of pushed-payload validation.
      request_type: The generated parameters type, used to serialize `request`.
      response_type: The generated payload type, used to validate each push.
    """
    values = (
      _json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    payload_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = self.client.authed_subscribe if meta.get('private', False) else self.client.subscribe
    return call(channel, values, validator=payload_validator, validate=validate)

  async def authed_command(
    self,
    req: 'Mapping[str, Any]',
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Send one id-correlated trade command (`place-order`/`cancel-order`); never called
    from generated code -- see this module's own docstring."""
    return await self.client.authed_command(req, validator=validator, validate=validate)
