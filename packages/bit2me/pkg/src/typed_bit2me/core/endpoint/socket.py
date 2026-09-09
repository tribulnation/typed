"""Base endpoint class for every `trading_ws` leaf reached over one `TradingWsClient`
connection: its six one-shot commands (`add_order`, `cancel_order`, ...) and its
channel subscriptions (`order_book`, `my_balance`, ...) alike.

One core class providing both `request()` (design §2) and `subscribe()` (design §8) is
needed because `trading_ws`'s own `router.json` resolves one core for the whole
directory, and that directory mixes both wire dialects on one physical connection
(`spec/core.md`'s Surfaces section) -- design §5's "a resolved core class only ever
needs to provide the call verb(s) actually exercised by the endpoints beneath its
position in the tree"; here that's both.

Declares no `meta` schema in `codegen/config.toml` -- authentication is a one-time,
connection-level `authenticate` handshake (`TradingWsClient.__aenter__`), never a
per-call decision, so every endpoint's own `meta` is `{}` and the generated call omits
`meta=` entirely (design §6: "a core with no `meta` schema means every endpoint
resolving to it must declare `meta: {}`")."""

from typing_extensions import Any, Protocol, Self, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T')


class SocketClient(Protocol):
  """Structural interface `TradingWsClient` implements to back a `SocketEndpoint`."""

  async def request(
    self,
    path: str,
    params: dict[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Send one of the six one-shot commands and await its reply."""
    ...

  def subscribe(
    self,
    channel: str,
    params: dict[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to a channel, validating each pushed notification against `validator`
    if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class SocketEndpoint:
  """Base class for every Trading Spot WebSocket endpoint reached over one
  `TradingWsClient` connection -- commands and channel subscriptions alike (design
  §2/§8's two verbs, `request`/`subscribe`, both provided by one core)."""

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
    """One `trading_ws` command/reply call (design §2's single verb) -- `path` is the
    wire command name (`add-order`, `cancel-order`, ...).

    Args:
      request: The generated `Request`/`Parameters` value (a `TypedDict` instance, or
        `None` for a command with no fields beyond its own `event`).
      path: The wire command name.
      validate: Per-call override of reply validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated reply type, used to validate the reply.
    """
    params = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    return await self.client.request(path, params, validator=response_validator, validate=validate)

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
      channel: The wire channel name (`order-book`, `my-balance`, ...).
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
    return self.client.subscribe(channel, params, validator=payload_validator, validate=validate)
