"""Transport-agnostic base for Bit2Me's channel-subscription endpoints
(`trading_ws`'s public/private channels)."""

from dataclasses import dataclass
from typing_extensions import Any, Mapping, Protocol, Self, TypeVar

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T')


class StreamClient(Protocol):
  """What a subscription endpoint needs from its transport: public or authenticated."""

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]: ...
  def authed_subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]: ...
  async def __aenter__(self) -> Self: ...
  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class StreamEndpoint:
  """Base for every hand-written or generated `trading_ws` subscription method."""

  client: StreamClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    return self.client.subscribe(
      channel, params, validator=validator, validate=validate
    )

  def authed_subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    return self.client.authed_subscribe(
      channel, params, validator=validator, validate=validate
    )
