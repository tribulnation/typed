"""Base endpoint class for KuCoin WebSocket channel endpoints.

`subscribe` backs a public topic, `authed_subscribe` a private one — the split KuCoin's
own connection-level public/private distinction naturally falls into, since one physical
connection serves both once it holds a private bullet token; see `spec/core.md`
§WebSocket. Both return an already-unwrapped, optionally-validated push, the streaming
analogue of `endpoint.rpc.RpcClient` unwrapping the REST envelope.
"""

from typing_extensions import Any, Protocol, Self, TypeVar
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class StreamClient(Protocol):
  """Structural interface a transport implements to back a `StreamEndpoint`."""

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
      AuthError: This connection was opened with no credentials — raised eagerly, before
        any network I/O, the same bar `RpcClient.authed_request` holds. KuCoin's
        private/public split is decided once, per connection (which bullet token
        authenticated it), so there is nothing a deferred `StreamManager.connect()`
        could learn any later that isn't already known at call time.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for KuCoin WebSocket channel endpoint classes/mixins."""

  client: StreamClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    return self.client.subscribe(channel, validator=validator, validate=validate)

  def authed_subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    return self.client.authed_subscribe(channel, validator=validator, validate=validate)
