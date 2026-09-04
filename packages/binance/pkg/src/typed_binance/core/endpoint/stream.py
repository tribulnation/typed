"""Base endpoint class for public (unauthenticated) market-data stream endpoints: design
§2/§8's single `subscribe()` verb. No `meta` schema declared for this core (`codegen/config.toml`
`[cores.stream]` is absent) -- every subscription is unauthenticated with no other
per-call quirk, so every endpoint resolving here declares `meta: {}`.

A generated method whose declared `parameters` are exactly `channel`'s own placeholders
(binance's own real, worked case -- 49 of its 53 stream endpoints, 2026-09 codegen
mechanization channel-params revision, `common/lib/src/typed_dev/codegen/python.py`'s
`Generator.stream_endpoint`) builds the channel string directly from its own already-typed
local variables, e.g. `f'{pair}@indexPriceKline_{interval}'` -- no `Parameters` object, no
`dump_request` detour. Binance's own wire convention wants a `symbol`/`pair` placeholder
lowercase; the caller passes the correctly-cased value themselves (every such parameter's
spec `description` states the requirement), and no implicit transform is applied here.
`subscribe()`'s own `channel.format(**values)` fallback still exists for the two shapes
that genuinely still need it: a template with no placeholders at all (`parameters` never
even declared), where the caller passes `parameters=None` and this just returns `channel`
unchanged; and, in principle, a client core built before this revision landed -- there's no
such endpoint left in this client's own spec today (0 of binance's real stream endpoints
declare a genuine extra, non-placeholder field the way dYdX's `batched` does), but
`subscribe()` keeps the general shape rather than assume that never changes.
"""

from typing_extensions import Any, Protocol, Self, TypeVar
from dataclasses import dataclass
from types import UnionType

from typed_core.util import StreamManager
from typed_core.validation import validator

from .wire import dump_request

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
    """Subscribe to a public channel, validating each notification against `validator` if given."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(frozen=True, kw_only=True)
class StreamEndpoint:
  """Base class for public market-data stream endpoints."""

  client: StreamClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self,
    channel: str,
    parameters: Any = None,
    *,
    meta: dict[str, Any] | None = None,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> 'StreamManager[T, Any, Any]':
    """Subscribe to one public channel: fill `channel`'s own `{placeholder}`s from
    `parameters` (design §8's "same placeholder-substitution rule as `path`"), then
    subscribe.

    Every one of this client's real generated stream endpoints with placeholders now
    builds its own channel string directly (`Generator.stream_endpoint`'s direct-channel
    path) and calls this with `channel` already fully resolved and `parameters`/
    `request_type` both left at their default `None` -- this path still exists for a
    template with no placeholders at all (`parameters` never declared) and as the general
    fallback a future endpoint needing a genuine extra, non-placeholder subscribe field
    (dYdX's `batched`-style case) would need.

    Args:
      channel: The channel template string (`endpoint.spec.channel`), e.g.
        `"{symbol}@bookTicker"`.
      parameters: The generated `Parameters` value filling `channel`'s placeholders, or
        `None` for a channel with none.
      meta: Unused -- this core declares no `meta` schema (every endpoint resolving here
        is unauthenticated with no other per-call quirk).
      validate: Per-call override of pushed-payload validation.
      request_type: The generated parameters type, used to serialize `parameters`.
      response_type: The generated payload type, used to validate each push.
    """
    values = dump_request(parameters, request_type) or {}
    resolved_channel = channel.format(**values) if values else channel
    response_validator = validator(response_type) if response_type is not None else None  # type: ignore[type-var]
    return self.client.subscribe(resolved_channel, validator=response_validator, validate=validate)
