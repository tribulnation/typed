"""Streams endpoint base: stream-shaped, WebSocket only, backed directly by the shared,
multiplexed `SocketClient` connection -- no `transport/` package here, unlike `info` and
`exchange`: `streams` has exactly one physical transport, so `SocketClient` (which already
satisfies `StreamClient` structurally) needs no adapter. See `spec/core.md` for the full
surface writeup.

A handful of Hyperliquid's WebSocket channels are shared across every concurrent
subscription regardless of scope (every coin's `l2Book` push arrives tagged just
`"l2Book"`), so a caller subscribed to more than one coin needs the *local* subscription
keyed by that scope and the resulting stream re-filtered to just it, since one shared
connection's subscription can otherwise receive another coin's pushes before its own
filter/key is installed -- `_SCOPE_FIELDS` is fixed per-venue wire knowledge design §2/§8
delegates to `core` (unlike `exchange`'s per-call quirks, this doesn't vary per endpoint
within `streams`, so it stays a plain hardcoded mapping rather than a declared `meta`
value). `_REQUEST_CHANNEL` covers `user_events`' own divergence: `endpoint.spec.channel`
records the *push* tag (`"user"`, per `docs/spec/authoring.md` rule 0 -- the wire identity
`core` keys pushes by), but the *subscribe* frame still needs the type `"userEvents"`.
"""

from typing_extensions import Any, Mapping, Self, TypeVar, cast
from types import UnionType
from dataclasses import dataclass
from datetime import timedelta

from typed_core.util import StreamManager
from typed_core.validation import validator

from typed_hyperliquid.core.endpoint.stream import StreamEndpoint
from typed_hyperliquid.core.urls import ws_url as resolve_ws_url
from typed_hyperliquid.core.wire import dump_request
from typed_hyperliquid.core.ws import SocketClient

T = TypeVar('T')

_ScopeField = tuple[str, str]
"""One `(subscribe field name, pushed-message field name)` pair a shared channel is
locally keyed and filtered by. Usually identical (`('coin', 'coin')`); `candle` differs
(`('coin', 's')`, `('interval', 'i')` -- the push tags the *market*, not the subscription)."""

_SCOPE_FIELDS: Mapping[str, list[_ScopeField]] = {
  'l2Book': [('coin', 'coin')],
  'bbo': [('coin', 'coin')],
  'activeAssetCtx': [('coin', 'coin')],
  'activeAssetData': [('user', 'user'), ('coin', 'coin')],
  'candle': [('coin', 's'), ('interval', 'i')],
  'trades': [('coin', 'coin')],
}
"""Wire channel -> the subscribe/message field pairs it's locally scoped by."""

_LIST_SHAPED: frozenset[str] = frozenset({'trades'})
"""Wire channels whose pushed messages are a list of items, scoped by the *first* item's
own fields rather than the message itself."""

_REQUEST_CHANNEL: Mapping[str, str] = {'user': 'userEvents'}
"""Wire channel (the push tag, `endpoint.spec.channel`) -> the distinct subscribe-frame
type, for the one channel where they diverge."""


@dataclass(kw_only=True)
class StreamsCore(StreamEndpoint):
  """Base for Hyperliquid WebSocket stream endpoint groups."""

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to one channel: dump `parameters` through its own validator, key and
    filter a shared-tag channel to its own scope when `channel` needs it, and validate
    each pushed message through `response_type`'s validator.

    No `meta` parameter: this core declares no `[cores.<name>].meta` schema in
    `codegen/config.toml` (design §2/§6) -- every Hyperliquid channel subscribes identically,
    with no per-channel credential or other quirk to decide (a `user` address is just an
    ordinary subscribe parameter). Every endpoint resolving to this core declares
    `meta: {}`.

    Args:
      channel: The wire channel/subscribe type (`endpoint.spec.channel`).
      parameters: The generated `Parameters` value, or `None` for a parameterless
        subscription.
      validate: Per-call override of pushed-message validation.
      request_type: The generated parameters type, used to serialize `parameters`.
      response_type: The generated payload type, used to validate each pushed message.
    """
    values = dump_request(parameters, request_type)
    scope = _SCOPE_FIELDS.get(channel)
    list_shaped = channel in _LIST_SHAPED
    subscribe_kwargs: dict[str, Any] = {}

    if scope is not None:
      key = ':'.join(str(values.get(sub, '')).lower() for sub, _ in scope)
      local_channel = f'{channel}:{key}'
      subscribe_kwargs['request_channel'] = channel

      def message_key(data: Any) -> str:
        source = data[0] if list_shaped else data
        local_key = ':'.join(
          str(source.get(msg_field, '')).lower() for _, msg_field in scope
        )
        return f'{channel}:{local_key}'

      subscribe_kwargs['message_key'] = message_key
    else:
      local_channel = channel
      if channel in _REQUEST_CHANNEL:
        subscribe_kwargs['request_channel'] = _REQUEST_CHANNEL[channel]

    stream = self.client.subscribe(local_channel, values or None, **subscribe_kwargs)

    if scope is not None:

      def match(msg: Any) -> bool:
        if list_shaped:
          if not msg or not isinstance(msg[0], dict):
            return False
          source = msg[0]
        else:
          source = msg
        return all(
          str(source.get(msg_field, '')).lower() == str(values.get(sub, '')).lower()
          for sub, msg_field in scope
        )

      stream = stream.filter(match)

    should_validate = self.validate if validate is None else validate
    if response_type is not None:

      def mapper(msg: Any) -> T:
        return (
          validator(cast(type, response_type)).python(msg) if should_validate else msg
        )

      stream = stream.map(mapper)

    return stream

  @classmethod
  def of(cls, ws: SocketClient, *, validate: bool = True) -> Self:
    """Create a Streams client from an existing WebSocket transport.

    Args:
      ws: Shared WebSocket transport.
      validate: Validate pushed messages.
    """
    return cls(client=ws, validate=validate)

  @classmethod
  def connect(
    cls,
    *,
    mainnet: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    validate: bool = True,
    ws_url: str | None = None,
  ) -> Self:
    """Create a Streams client, opening its own WebSocket transport.

    Args:
      mainnet: Use mainnet when true, testnet when false.
      timeout: WebSocket request timeout.
      validate: Validate pushed messages.
      ws_url: Custom WebSocket URL. If provided, takes precedence over `mainnet`.
    """
    ws = SocketClient(url=ws_url or resolve_ws_url(mainnet), timeout=timeout)
    return cls.of(ws, validate=validate)

  @classmethod
  def new(cls, client: SocketClient, *, validate: bool = True) -> Self:
    """Build a Streams core forwarding a root client's already-built WebSocket transport
    (design §5a) -- not meant to be called directly; `client.streams`'s generated
    `@cached_property` calls this, forwarding `ClientBase.validate` by name.

    Args:
      client: The shared WebSocket transport.
      validate: Validate pushed messages.
    """
    return cls(client=client, validate=validate)
