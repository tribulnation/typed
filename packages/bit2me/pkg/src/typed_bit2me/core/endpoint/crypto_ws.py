"""Base endpoint class for bit2me's `crypto_ws` surface: one `authenticate` command with
no reply of its own (`spec/core.md`'s Authentication section -- "silence means it
worked"), then every notification type the account is entitled to arrives unprompted on
the same firehose, dispatched by its own `type` field (`docs/spec/authoring.md` rule 11's
`push: {"trigger": "after_rpc"}`). One core class providing both `request()` (the
`authenticate` command) and `subscribe()` (the notification firehose) is needed for the
same reason `SocketEndpoint` provides both for `trading_ws`: `crypto_ws`'s own
`router.json` resolves one core for the whole directory, mixing both wire dialects on one
physical connection (`spec/core.md`'s Surfaces section).
"""

from typing_extensions import Any, Protocol, Self, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T')


class CryptoWsSocketClient(Protocol):
  """Structural interface `CryptoWsClient` implements to back a `CryptoWsEndpoint`."""

  async def request(self, path: str, params: dict[str, Any] | None = None):
    """Send a command frame. `crypto_ws` sends no reply for any command it defines --
    `authenticate`'s own success case is silent ('silence means it worked')."""
    ...

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Every notification received on this connection's single firehose, validating
    each one against `validator` if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class CryptoWsEndpoint:
  """Base class for every `crypto_ws` endpoint reached over one `CryptoWsClient`
  connection -- the `authenticate` command and the notification firehose alike."""

  client: CryptoWsSocketClient

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
  ):
    """Send `path`'s command frame (design §2's single verb) -- `crypto_ws` defines no
    command with a reply of its own, so unlike `RpcEndpoint`/`SocketEndpoint` this
    never returns a validated value (see `spec/core.md`'s Authentication section).

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        command with no fields beyond its own `type`).
      path: The wire command name (`authenticate`).
      validate: Unread -- accepted only for call-shape consistency with every other
        generated `rpc` endpoint method (S8); there is no reply to validate here.
      request_type: The generated request type, used to serialize `request`.
    """
    params = (
      json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    await self.client.request(path, params)

  def subscribe(
    self,
    channel: str,
    request: Any = None,
    *,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Every notification pushed on this connection's single firehose (design §2/§8's
    `subscribe` verb) -- `crypto_ws` has no subscribe/unsubscribe protocol of its own
    (`spec/core.md`'s Surfaces section), so unlike `SocketEndpoint.subscribe` this
    never sends a wire frame; `channel`/`request`/`request_type` are accepted only for
    call-shape consistency with `stream_endpoint`'s generated call.

    Args:
      channel: The wire channel template string (`endpoint.spec.channel`) -- unread,
        `crypto_ws` has exactly one firehose per connection, nothing to route on.
      request: The generated `Parameters` value -- unread, this firehose takes none.
      validate: Per-call override of pushed-payload validation.
      request_type: Unread -- see `request` above.
      response_type: The generated payload type, used to validate each push.
    """
    response_validator = validator(cast(type, response_type)) if response_type is not None else None
    return self.client.subscribe(channel, validator=response_validator, validate=validate)
