"""Base endpoint class for RPC endpoints -- shared by `info` and `exchange`, the two
surfaces reachable over either HTTP or the shared WebSocket connection, both with the
same request/reply shape: one JSON payload in, one decoded value out.

No `method`/`path` decomposition here: Hyperliquid has exactly one URL per surface
(`/info`, `/exchange`) and selects the operation via a `type` field inside the payload,
not the URL. No `authed_request` split either -- `exchange`'s "authentication" is a
signature embedded in the payload itself (see `exchange/core/auth.py`), built one layer
above this class, not a header a transport attaches generically.

Not frozen, unlike the generic template: every leaf endpoint method (`info.l2_book`,
`exchange.order`, ...) is its own single-method mixin, and `Info`/`Exchange`/`Streams`
compose ~20-100 of them via multiple inheritance into one flat, `type`-discriminated
namespace matching the venue's own flat request shape -- not nested `cached_property`
subsections. Python's `dataclasses` requires every class in an inheritance chain to
agree on frozen-ness, so freezing this base would force freezing that entire composed
chain for no behavioral benefit (nothing here is ever mutated post-construction).
"""

from typing_extensions import Any, Mapping, Protocol, Self
from dataclasses import dataclass


class RpcClient(Protocol):
  """Structural interface a transport implements to back an `RpcEndpoint`."""

  async def request(self, payload: Mapping[str, Any]) -> Any:
    """Send one request payload and return the decoded response value."""
    ...

  async def __aenter__(self) -> Self: ...

  async def __aexit__(self, exc_type, exc_value, traceback): ...


@dataclass(kw_only=True)
class RpcEndpoint:
  """Base class for RPC endpoints."""

  client: RpcClient
  validate: bool = True

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(self, payload: Mapping[str, Any]) -> Any:
    return await self.client.request(payload)
