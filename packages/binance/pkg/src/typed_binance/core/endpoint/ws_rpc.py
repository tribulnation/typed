"""Base endpoint class for WS-API-shaped RPC endpoints -- `{method, params}` requests, with
no separate HTTP-verb/path pair the way `endpoint/rpc.py`'s REST shape has. `path` (the
generated call's own wire identifier, design §2/§7) doubles as the JSON-RPC `method` name
here; a WS-only operation declares no HTTP verb (`spec.method` is unset), so the generated
call never passes one.

Also carries `subscribe`: Binance's WS API connection can be upgraded, via a signed
`userDataStream.subscribe.signature` call, to also push this account's order/balance events
on the same connection -- the one place a Binance WS surface is genuinely both RPC- and
stream-shaped at once (see `spec/core.md`'s WebSocket section). Spot's `spot/ws/user_data/
events/endpoint.json` spec's this as an ordinary `kind: 'stream'` endpoint (`docs/spec/
authoring.md` rule 11's `push: {"trigger": "after_rpc"}`, gated on the sibling
`user_data.subscribe_signature` RPC endpoint), generated the same way `endpoint/stream.py`'s
`StreamEndpoint.subscribe`/`endpoint/private_stream.py`'s `PrivateStreamEndpoint.subscribe`
already are -- this `subscribe` is that same design §2/§8 verb, not a hand-written escape
hatch. USD-M/COIN-M's WS API has no equivalent mechanism (`userDataStream.start`/`.ping`/
`.stop`, listenKey-based, is a structurally distinct family -- see `spec/core.md`'s
Surfaces section and `spec/discovery.md` §9), so no `kind: 'stream'` endpoint resolves to
this core for those two products; `subscribe` stays reachable there only because it lives
on this shared base class, unused.
"""

from typing_extensions import Any, Mapping, NotRequired, Protocol, Self, TypedDict, TypeVar
from dataclasses import dataclass
from types import UnionType

from typed_core.util import StreamManager
from typed_core.validation import validator

from .wire import dump_request, wire_params

T = TypeVar('T', default=Any)


class Meta(TypedDict):
  """`ws_rpc`'s own `meta` shape (`codegen/config.toml` `[cores.ws_rpc].meta`) -- identical to
  `endpoint/rpc.py`'s `Meta`, kept as its own hand-written declaration since each resolved
  core's module is self-contained (design §2/§6)."""

  security: NotRequired[str]
  """Binance's documented security-tier label -- `TRADE`, `USER_DATA`, `MARGIN`, `SIGNED`,
  `MARKET_DATA`, `USER_STREAM`, `NONE`, or `System`."""
  signed: NotRequired[bool]
  """Whether this call must be HMAC-signed."""


class WsRpcClient(Protocol):
  """Structural interface a transport implements to back a `WsRpcEndpoint`."""

  async def request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def authed_request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  async def keyed_request(
    self,
    method: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T: ...

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]': ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class WsRpcEndpoint:
  """Base class for WS-API-shaped RPC endpoints (Binance's Spot/USD-M/COIN-M WS API)."""

  client: WsRpcClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one WS API call: serialize `request` through `request_type`'s validator
    (ADR 0020/S28) into the JSON `params` object, and dispatch to `self.client.request`/
    `.keyed_request`/`.authed_request` per the identical three-tier security dispatch
    `endpoint/rpc.py`'s `RpcEndpoint.request` uses -- see that method's own docstring.

    Args:
      request: The generated `Request` value, or `None` for a parameterless operation.
      path: The wire JSON-RPC method name (`endpoint.spec.path`).
      meta: This call's own quirks -- security tier and signing requirement.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    values = dump_request(request, request_type)
    params, _lang = wire_params(values)
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    if meta.get('signed', False):
      return await self.client.authed_request(
        path, params, validator=response_validator, validate=validate
      )
    security = meta.get('security')
    if security in ('NONE', None, 'System'):
      return await self.client.request(
        path, params, validator=response_validator, validate=validate
      )
    return await self.client.keyed_request(
      path, params, validator=response_validator, validate=validate
    )

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe this connection to `channel`'s push events (design §2/§8's single
    `subscribe()` verb).

    Unlike `request()`, this doesn't branch on `meta`: the WS API exposes exactly one
    subscribable channel per connection (`spot.ws.user_data.events`'s own `channel`,
    `"userData"`), and its subscribe/unsubscribe RPC calls are already hardcoded at the
    transport level (`SocketRpc.request_subscription`/`.request_unsubscription`,
    `core/transport/ws/api.py`), including their own signing requirement -- `meta` is
    accepted here only for call-shape consistency with this core's declared
    `[cores.ws_rpc].meta` schema (`codegen/config.toml`), matching `request()`'s identical
    parameter. `parameters`/`request_type` are likewise accepted for shape parity with
    `endpoint/stream.py`'s `StreamEndpoint.subscribe` even though this channel takes no
    wire parameters of its own.

    Args:
      channel: The channel template string (`endpoint.spec.channel`), always `"userData"`
        for this core today.
      parameters: The generated `Parameters` value, or `None` for a parameterless channel.
      meta: This subscription's own declared quirks -- unread, see above.
      validate: Per-call override of pushed-payload validation.
      request_type: The generated parameters type, used to serialize `parameters`.
      response_type: The generated payload type, used to validate each push.
    """
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(channel, validator=response_validator, validate=validate)
