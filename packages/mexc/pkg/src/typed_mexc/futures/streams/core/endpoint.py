"""Base endpoint class for every MEXC Futures WebSocket leaf -- the resolved
`futures_streams_endpoint` core (`codegen/config.toml`). Every real Futures push is plain
JSON (`{channel, data, ts}`, already unwrapped to `data` by `parse_msg`), so -- unlike
Spot's protobuf-narrowed streams -- these render normally through the universal
`stream_endpoint`: no per-call quirk beyond which physical connection (public market
vs private, login-gated user) `[python.cores.futures_streams].children` already
forwards, so no `meta` schema is declared for this core at all (`codegen/config.toml`).
"""

from typing_extensions import Any, Protocol, Self, TypeVar, cast
from dataclasses import dataclass
from types import UnionType
import json

from typed_core.util import StreamManager
from typed_core.validation import validator

T = TypeVar('T')


class FuturesStreamsClient(Protocol):
  """Structural interface both `FuturesPublicStreamsClient` and
  `FuturesPrivateStreamsClient` satisfy."""

  def subscribe(self, channel: str, params: Any = None) -> StreamManager[Any, Any, Any]: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class FuturesStreamsEndpoint:
  """Base class for every MEXC Futures WebSocket leaf reached over one
  `FuturesStreamsClient` connection (public market data or private, login-gated user
  data alike)."""

  client: FuturesStreamsClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

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
      channel: The wire channel/method name, already fully substituted.
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
    manager = self.client.subscribe(channel, params)
    if response_type is None:
      return cast(StreamManager[T, Any, Any], manager)
    payload_validator = validator(cast(type, response_type))
    if not self._should_validate(validate):
      return cast(StreamManager[T, Any, Any], manager)
    return manager.map(payload_validator.python)

  def _should_validate(self, validate: bool | None) -> bool:
    return True if validate is None else validate
