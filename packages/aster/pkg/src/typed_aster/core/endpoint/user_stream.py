"""Base endpoint class for the listenKey user-data stream of each surface.

There is no subscribe frame: connecting to `/ws/<listenKey>` is the subscription, and
every account event is pushed on it. The listenKey itself comes from the surface's REST
`listenKey` endpoints (create, keep alive every < 60 minutes, close).
"""

from typing_extensions import Any, Protocol, Self, TypeVar
from dataclasses import dataclass
from types import UnionType

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class UserStreamClient(Protocol):
  """Structural interface a transport implements to back a `UserStreamEndpoint`."""

  def connect(
    self,
    listen_key: str,
    *,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> 'StreamManager[T, None, None]':
    """Open the user-data connection for `listen_key`, validating each event if asked."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class UserStreamEndpoint:
  """Base class for user-data stream endpoints."""

  client: UserStreamClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    listen_key: str,
    *,
    validate: bool | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, None, None]':
    """Open the user-data connection for `listen_key`.

    Args:
      listen_key: A live listenKey from the surface's REST `listenKey` endpoint.
      validate: Per-call override of event validation.
      response_type: The generated event type, used to validate each push.
    """
    if not listen_key:
      raise ValueError('listen_key is required')
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return self.client.connect(
      listen_key, validator=response_validator, validate=validate
    )
