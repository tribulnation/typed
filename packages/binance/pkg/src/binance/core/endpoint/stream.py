"""Base endpoint class for stream endpoints."""

from typing_extensions import Any, Protocol, Self, TypeVar
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class StreamClient(Protocol):
  """Structural interface a transport implements to back a `StreamEndpoint`. No
  `authed_subscribe`: Binance's private user-data streams don't sign the *same*
  connection the way `RpcClient.authed_request` signs the same HTTP client — they need a
  separate `listenKey` connection instead (see `spec/core.md`'s Authentication section),
  not implemented yet.
  """

  def subscribe(
    self,
    channel: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a public channel, validating each notification against `validator` if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for stream endpoints."""

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
