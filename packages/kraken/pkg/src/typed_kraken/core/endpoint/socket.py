"""Base endpoint class for every one of Kraken's WebSocket v2 leaves reached over one
`KrakenSocketClient` connection: trading-method request/reply calls (`trading_ws.*`,
`streams.market_data.ping`) and channel subscriptions (`streams.market_data.*` other
than `ping`, `streams.private.*`) alike.

One core class providing both `request()` (design §2) and `subscribe()` (design §8) is
needed because a `router.json`'s `core` resolves once per directory, and
`streams.market_data` itself mixes both wire dialects -- `ping` (request/reply) among
six channel subscriptions -- so its own resolved core needs both verbs (design §5's "a
resolved core class only ever needs to provide the call verb(s) actually exercised by
the endpoints beneath its position in the tree"; here that's both, not because every
single leaf needs both, but because the directory as a whole does).
"""

from typing_extensions import Any, Protocol, Self, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T')

RAW_METHODS = {'ping', 'batch_cancel'}
"""WS commands whose reply is the whole frame, not nested under `result` -- neither
declares `envelope` (see each endpoint's own spec `notes`). A fixed per-path table, the
same shape `core/endpoint/rpc.py`'s `JSON_BODY_PATHS` uses."""


class SocketClient(Protocol):
  """Structural interface `KrakenSocketClient` implements to back a `SocketEndpoint`."""

  async def request(
    self,
    method: str,
    params: dict[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Call a WebSocket RPC method and await its `req_id`-correlated reply, returning
    the reply's `result` field."""
    ...

  async def raw_request(
    self,
    method: str,
    params: dict[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Call a WebSocket RPC method and await its `req_id`-correlated reply, returning
    the whole reply frame -- for `RAW_METHODS`."""
    ...

  def subscribe(
    self,
    channel: str,
    params: dict[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to a channel, validating each notification against `validator` if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class SocketEndpoint:
  """Base class for every Kraken WebSocket v2 endpoint reached over one
  `KrakenSocketClient` connection -- trading-method calls and channel subscriptions
  alike (design §2/§8's two verbs, `request`/`subscribe`, both provided by one core)."""

  client: SocketClient

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
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """One WS command/reply call (design §2's single verb) -- `path` is the wire method
    name (`add_order`, `ping`, ...); the reply nests under `result` unless `path` is one
    of `RAW_METHODS`, whose reply is the whole frame.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      path: The wire method name.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    params = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = self.client.raw_request if path in RAW_METHODS else self.client.request
    return await call(path, params, validator=response_validator, validate=validate)

  def subscribe(
    self,
    channel: str,
    request: Any = None,
    *,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> StreamManager[T, Any, Any]:
    """One channel subscription (design §2/§8's `subscribe` verb).

    Args:
      channel: The wire channel name/template.
      request: The generated `Parameters` value (a `TypedDict` instance, or `None`).
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
    return self.client.subscribe(
      channel, params, validator=payload_validator, validate=validate
    )
