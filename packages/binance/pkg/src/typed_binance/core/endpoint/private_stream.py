"""Base endpoint class for private (listenKey-based) user-data stream endpoints."""

from typing_extensions import Any, Protocol, Self, TypeVar
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class PrivateStreamClient(Protocol):
  """Structural interface a transport implements to back a `PrivateStreamEndpoint`.

  Unlike `StreamClient.subscribe`, there is no channel to name: connecting with a live
  listenKey already embedded in the URL path *is* the subscription, and the server starts
  pushing whichever of several event types occur, with no way to select a subset (see
  `spec/core.md`'s WebSocket section).
  """

  def connect(
    self,
    listen_key: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, None, None]':
    """Open one private user-data connection for `listen_key`, validating each pushed
    event against `validator` if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class PrivateStreamEndpoint:
  """Base class for private (listenKey-based) user-data stream endpoints."""

  client: PrivateStreamClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def connect(
    self,
    listen_key: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, None, None]':
    return self.client.connect(listen_key, validator=validator, validate=validate)
