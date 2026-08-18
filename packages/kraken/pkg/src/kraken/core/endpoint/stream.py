"""Base endpoint class for Kraken's WebSocket channel subscriptions.

Unlike the HTTP surface, whether a channel needs auth is a property of which physical
connection the backing client was built for (`ws.kraken.com/v2` vs
`ws-auth.kraken.com/v2` -- see `transport/ws.py`), not a per-call flag: Kraken's private
channels take no separate `authed_subscribe`, only a `token` merged into the same
`subscribe` params. So, unlike the generic template this was adapted from, there is only
one subscribe method here.
"""

from typing_extensions import Any, Mapping, Protocol, Self, TypeVar
from dataclasses import dataclass

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T', default=Any)


class StreamClient(Protocol):
  """Structural interface a socket transport implements to back a `StreamEndpoint`."""

  def subscribe(
    self,
    channel: str,
    params: Mapping[str, Any] | None = None,
    *,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    """Subscribe to a channel, validating each notification against `validator` if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for Kraken WebSocket channel-subscription endpoints."""

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
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> StreamManager[T, Any, Any]:
    return self.client.subscribe(
      channel, params, validator=validator, validate=validate
    )
