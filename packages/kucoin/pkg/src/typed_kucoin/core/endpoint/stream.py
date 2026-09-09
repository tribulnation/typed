"""Base endpoint classes for KuCoin WebSocket channel endpoints (design §2/§8's single
`subscribe()` verb).

`PublicStreamEndpoint`/`PrivateStreamEndpoint` are the resolved `stream_public`/
`stream_private` cores (`codegen/config.toml`) -- public-vs-private is a genuine directory-level
fact (which spec subtree an endpoint lives under), never a per-call `meta` quirk, the
same reasoning kraken's own `socket` core and binance's `stream`/`private_stream` split
already establish. Both classes hold the identical `client: StreamClient` field type --
one physical `SocketStreamClient` connection serves both public and private topics once
it's opened with a private bullet token (`core/transport/ws.py`'s own docstring) -- and
differ only in which of `subscribe`/`authed_subscribe` they call.
"""

from typing_extensions import Any, Protocol, Self, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.util import StreamManager
from typed_core.validation import validator

from .wire import substitute_template

T = TypeVar('T', default=Any)


class StreamClient(Protocol):
  """Structural interface a transport implements to back a stream endpoint."""

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a public topic, validating each push against `validator` if given."""
    ...

  def authed_subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a private topic, validating each push against `validator` if given.

    Raises:
      AuthError: This connection was opened with no credentials.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


def _dump_params(request: Any, request_type: type[Any] | UnionType | None) -> dict[str, Any] | None:
  """Serialize a generated `Parameters` value through its own validator (ADR 0020/S28)
  into a plain dict."""
  if request_type is None or request is None:
    return None
  return json.loads(validator(cast(type, request_type)).dump(request))


@dataclass(kw_only=True, frozen=True)
class PublicStreamEndpoint:
  """Base class for a public KuCoin WebSocket channel -- the resolved `stream_public`
  core for every unauthenticated stream subtree (`codegen/config.toml`)."""

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
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> StreamManager[T, Any, Any]:
    """One public channel subscription (design §2/§8's `subscribe` verb): fills any
    `{placeholder}` segment of `channel` from the serialized `Parameters` value (design
    §7 -- derived from the template string itself, never a spec-declared role marker).

    Args:
      channel: The wire topic string/template.
      request: The generated `Parameters` value (a `TypedDict` instance, or `None`).
      validate: Per-call override of pushed-payload validation.
      request_type: The generated parameters type, used to serialize `request`.
      response_type: The generated payload type, used to validate each push.
    """
    values = _dump_params(request, request_type)
    channel, _ = substitute_template(channel, values)
    payload_validator = validator(cast(type, response_type)) if response_type is not None else None
    return self.client.subscribe(channel, validator=payload_validator, validate=validate)


@dataclass(kw_only=True, frozen=True)
class PrivateStreamEndpoint:
  """Base class for a private KuCoin WebSocket channel -- the resolved `stream_private`
  core for every authenticated stream subtree (`codegen/config.toml`)."""

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
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> StreamManager[T, Any, Any]:
    """One private channel subscription (design §2/§8's `subscribe` verb): fills any
    `{placeholder}` segment of `channel` from the serialized `Parameters` value (design
    §7 -- derived from the template string itself, never a spec-declared role marker).

    Args:
      channel: The wire topic string/template.
      request: The generated `Parameters` value (a `TypedDict` instance, or `None`).
      validate: Per-call override of pushed-payload validation.
      request_type: The generated parameters type, used to serialize `request`.
      response_type: The generated payload type, used to validate each push.

    Raises:
      AuthError: This connection was opened with no credentials -- this is a private
        channel, unreachable from a `public=True` client.
    """
    values = _dump_params(request, request_type)
    channel, _ = substitute_template(channel, values)
    payload_validator = validator(cast(type, response_type)) if response_type is not None else None
    return self.client.authed_subscribe(channel, validator=payload_validator, validate=validate)
