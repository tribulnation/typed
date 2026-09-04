"""Base endpoint class for Deribit's channel-subscription surface -- the resolved
`streams` core (`codegen/config.toml`, design §5)."""

from typing_extensions import (
  Any,
  Mapping,
  NotRequired,
  Protocol,
  Self,
  TypedDict,
  TypeVar,
  cast,
)
from types import UnionType
from dataclasses import dataclass
import json
import re

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)

PLACEHOLDER = re.compile(r'\{([^{}]+)\}')
"""A `{name}` template slot inside a channel string (design §7/§8's location-marker
elimination) -- `book.{instrument_name}.{interval}`, `block_rfq.maker.{currency}`, and
every other parameterized Deribit channel encode every one of their declared
`parameters` fields this way, confirmed fleet-wide (no stream endpoint has a field left
over needing a separate subscribe-frame payload) -- Deribit's own wire subscribe frame
(`SocketConnection.request_subscription`) only ever sends the already-resolved channel
name, never a parameters object alongside it."""


class StreamClient(Protocol):
  """Structural interface a transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a public channel, validating each notification against `validator`
    if given."""
    ...

  def authed_subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a private (`user.*`) channel, validating each notification against
    `validator` if given.

    Raises:
      AuthError: This transport was built with no credentials. Raised lazily, once the
        returned `StreamManager` is actually connected.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


class Meta(TypedDict):
  """`streams`' own `meta` shape (`codegen/config.toml` `[cores.streams].meta`): whether this
  channel is public. Hand-written to match that declared JSON Schema -- never
  code-generated (design §2/§6, S27's own precedent)."""

  public: NotRequired[bool]
  """`True` for a public channel, subscribed with no credentials. Absent (or `False`)
  for a private (`user.*`) channel, which needs a fetched `access_token`."""


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for Deribit channel-subscription endpoint groups -- the resolved
  `streams` core."""

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
    request_type: type[Any] | UnionType | object | None = None,
    response_type: type[T] | UnionType | object | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """One channel subscription (design §2/§8's `subscribe` verb) -- public
    (`client.subscribe`) or private (`client.authed_subscribe`) per `meta['public']`.

    `channel` is the raw template as declared in the spec (e.g.
    `book.{instrument_name}.{interval}`) -- substituting its `{name}` placeholders from
    `request`'s own wire-serialized fields is this client's own job (design §7's "no
    per-parameter wire-placement logic runs [in codegen]"), the same wire-mechanics
    decision `RpcEndpoint.request` already makes for `path`. Every parameterized Deribit
    channel encodes every one of its declared fields this way, so there is no separate
    subscribe-frame payload to send alongside the resolved channel name.

    Args:
      channel: The wire channel name template.
      request: The generated `Parameters` value, or `None` for a channel with no
        subscribe-time fields.
      meta: This channel's own quirks -- `public` picks the subscribe method.
      validate: Per-call override of pushed-payload validation.
      request_type: The generated parameters type, used to serialize `request`.
      response_type: The generated payload type, used to validate each push. Typed
        `type[T] | UnionType | object | None` -- see `RpcEndpoint.request`'s identical
        parameter docstring for why the `object` fallback is needed (a pyright
        limitation specific to a single-value `Literal[...]` payload type, confirmed
        live, not a codegen defect).
    """
    values = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else {}
    )
    resolved_channel = PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), channel)
    payload_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = (
      self.client.subscribe
      if meta.get('public', False)
      else self.client.authed_subscribe
    )
    return call(resolved_channel, validator=payload_validator, validate=validate)
