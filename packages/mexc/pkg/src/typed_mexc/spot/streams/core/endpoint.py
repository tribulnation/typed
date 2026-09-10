"""Base endpoint class for every MEXC Spot WebSocket leaf -- the resolved
`spot_streams_endpoint` core (`codegen/config.toml`). Every real Spot push is a
protobuf-framed `PushDataV3ApiWrapper` narrowed to one of its own fields
(`meta['proto_field']`) -- the reason every one of these 9 leaves stays hand-written
(`surface: handwritten`, see each endpoint's own spec `surface.reason`): the real
runtime payload is the compiled `betterproto2` class narrowed off that field, and
`stream_endpoint`'s JSON-schema-driven `response_type` rendering has no equivalent of
gRPC's own `_grpc_proto_module` external-class resolution to bind a generated type name
to it safely. `subscribe()` still centralizes the one real mechanism every leaf needs
(filter+map on `meta['proto_field']`), so each hand-written leaf is a two-line call.
"""

from typing_extensions import Any, Protocol, Self, TypedDict
from dataclasses import dataclass

from typed_core.util import StreamManager

from .proto import PushDataV3ApiWrapper


class Meta(TypedDict):
  """`spot_streams_endpoint`'s own `meta` shape (`codegen/config.toml`
  `[cores.spot_streams_endpoint].meta`): which `PushDataV3ApiWrapper` field this
  channel's push narrows to. Required -- every real Spot push is protobuf-framed."""

  proto_field: str
  """Envelope field this channel's push narrows to, e.g. `public_spot_kline`."""


class SpotStreamsClient(Protocol):
  """Structural interface both `SpotPublicStreamsClient` and
  `SpotPrivateStreamsClient` satisfy: MEXC's private feed is the public one plus a
  `listenKey` query parameter, so both hand back the same envelope type."""

  def subscribe(
    self, channel: str, params: Any = None,
  ) -> StreamManager[PushDataV3ApiWrapper, Any, Any]: ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True, frozen=True)
class SpotStreamsEndpoint:
  """Base class for every MEXC Spot WebSocket leaf reached over one
  `SpotStreamsClient` connection (public market data or private, listen-key-managed
  user data alike)."""

  client: SpotStreamsClient

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  def subscribe(
    self, channel: str, *, meta: Meta,
  ) -> StreamManager[Any, Any, Any]:
    """Subscribe to one channel and narrow every push down to `meta['proto_field']`,
    dropping any push where that field is absent (a different oneof-style branch of
    the shared envelope).

    Args:
      channel: The wire channel name/template, already fully substituted.
      meta: This call's own quirk -- which envelope field to narrow to.
    """
    field = meta['proto_field']
    manager = self.client.subscribe(channel)
    return manager.filter(lambda wrapper: getattr(wrapper, field) is not None).map(
      lambda wrapper: getattr(wrapper, field)
    )
