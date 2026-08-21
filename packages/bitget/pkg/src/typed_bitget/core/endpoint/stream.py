"""Base endpoint class for stream (WebSocket) endpoints."""

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
    params: 'Mapping[str, Any] | None' = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a public channel, validating each notification against `validator` if given."""
    ...

  def authed_subscribe(
    self,
    channel: str,
    params: 'Mapping[str, Any] | None' = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to a private channel, validating each notification against `validator` if given.

    Raises:
      AuthError: This transport was built with no credentials. Raised lazily, once the
        returned `StreamManager` is actually connected (the login handshake it triggers is
        itself lazy, on first private subscribe on this connection).
    """
    ...

  async def authed_command(
    self,
    req: 'Mapping[str, Any]',
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Send one id-correlated trade command (`place-order`/`cancel-order`) and return its
    reply, validating it against `validator` if given.

    Raises:
      AuthError: This transport was built with no credentials.
    """
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
    params: 'Mapping[str, Any] | None' = None,
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
    params: 'Mapping[str, Any] | None' = None,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    return self.client.authed_subscribe(
      channel, params, validator=validator, validate=validate
    )

  async def authed_command(
    self,
    req: 'Mapping[str, Any]',
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    return await self.client.authed_command(req, validator=validator, validate=validate)
