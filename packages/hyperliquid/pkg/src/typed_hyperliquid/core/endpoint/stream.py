"""Base endpoint class for stream endpoints -- backs `streams`, the venue's only
channel-subscription surface.

No `authed_subscribe`: every Hyperliquid channel, public or user-scoped, subscribes with
a plain `user` address parameter (see `spec/discovery.md`'s Authentication section) --
there is no channel that additionally requires a wallet signature to open.

Not frozen, for the same reason as `endpoint/rpc.py`: `Streams` composes ~20 single-method
mixins via multiple inheritance rather than nested `cached_property` children, and
`dataclasses` requires frozen-ness to agree across that whole chain.

`StreamEndpoint` itself supplies only lifecycle (`client`, `validate`,
`__aenter__`/`__aexit__`) -- the design §2/§8 `.subscribe(channel, parameters, ...)` call
every generated leaf makes is defined on `StreamsCore` (`streams/core.py`), not here, so
its own generated parameter name (`parameters`) doesn't have to match this Protocol's
low-level `params` at all.
"""

from typing_extensions import Any, Callable, Protocol, Self
from dataclasses import dataclass

from typed_core.util import StreamManager


class StreamClient(Protocol):
  """Structural interface a transport implements to back a `StreamEndpoint`.

  `params` is `Any`, not `Mapping[str, Any]`: the concrete transport (`SocketClient`,
  shared with `info`/`exchange`) subscribes through `typed_core.ws.StreamsRpc`, whose own
  `params` is a specific `TypedDict` rather than an arbitrary mapping -- a `TypedDict`
  accepts a stricter set of values than `Mapping[str, Any]`, so typing this any narrower
  here would make that real implementation fail Protocol conformance.
  """

  def subscribe(
    self,
    channel: str,
    params: Any = None,
    *,
    request_channel: str | None = None,
    message_key: Callable[[Any], str] | None = None,
  ) -> StreamManager[Any, Any, Any]:
    """Subscribe to a channel, optionally separating request and message channels.

    `message_key`: for channels shared across multiple concurrent subscriptions (e.g.
    `l2Book`, tagged identically for every coin), a function deriving the local
    subscription key from an incoming notification.
    """
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True)
class StreamEndpoint:
  """Base class for stream endpoints."""

  client: StreamClient
  validate: bool = True

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)
