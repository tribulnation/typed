"""Base endpoint class for WebSocket stream (channel subscription) endpoints: design §2/§8's
single `subscribe()` verb, deciding public-vs-signed purely from `meta['signed']` -- every
generated call's own `meta` dict literal, matching `codegen/config.toml`'s `[cores.app_streams]`/
`[cores.exchange_streams]` meta schema.

Shared, auth-agnostic: both Coinbase App's `market_data`/`user` connections and Coinbase
Exchange's single WebSocket Feed connection resolve to this exact class -- only the
pre-built `client` transport and the venue-specific `meta` schema differ per subtree
(design §5)."""

from typing_extensions import Any, NotRequired, Protocol, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class Meta(TypedDict):
  """`app_streams`'s and `exchange_streams`'s shared `meta` shape (`codegen/config.toml`
  `[cores.app_streams]`/`[cores.exchange_streams]`): whether this channel needs a signed
  subscribe. Hand-written to match that declared JSON Schema -- never code-generated
  (design §2/§6, same precedent as `core.endpoint.rpc.Meta`)."""

  signed: NotRequired[bool]
  """Whether this channel needs a signed/authenticated subscribe (absent/`False` for
  every public channel)."""


class StreamClient(Protocol):
  """Structural interface a transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    channel: str,
    params: 'dict[str, Any] | None' = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a public channel, validating each notification against `validator` if given."""
    ...

  def authed_subscribe(
    self,
    channel: str,
    params: 'dict[str, Any] | None' = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a private channel, validating each notification against `validator` if given.

    Raises:
      AuthError: This transport was built with no credentials. Raised lazily, once the
        returned `StreamManager` is actually connected.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for every Coinbase WebSocket stream endpoint -- the resolved `core` for
  both `app`'s and `exchange`'s own streams subtrees (design §5)."""

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
    """One channel subscription (design §2/§8's `subscribe` verb).

    Args:
      channel: The wire channel name/template.
      request: The generated `Parameters` value (a `TypedDict` instance, or `None`).
      meta: This call's own quirks -- whether the channel needs a signed subscribe.
      validate: Per-call override of pushed-payload validation.
      request_type: The generated parameters type, used to serialize `request`.
      response_type: The generated payload type, used to validate each push.
    """
    params = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    payload_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = self.client.authed_subscribe if meta.get('signed', False) else self.client.subscribe
    return call(channel, params, validator=payload_validator, validate=validate)
