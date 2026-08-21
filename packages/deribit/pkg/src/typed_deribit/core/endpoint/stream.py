"""Base endpoint class for Deribit's channel-subscription surface."""

from typing_extensions import Any, Mapping, Protocol, Self, TypeVar
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


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


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for Deribit channel-subscription endpoint groups."""

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
  ) -> 'StreamManager[T, Any, Any]':
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
  ) -> 'StreamManager[T, Any, Any]':
    return self.client.authed_subscribe(
      channel, params, validator=validator, validate=validate
    )
