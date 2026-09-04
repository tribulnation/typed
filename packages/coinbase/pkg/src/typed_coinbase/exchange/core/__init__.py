"""Coinbase Exchange client core: HTTP + WebSocket Feed transport, HMAC authentication, and
error mapping — structurally distinct from `typed_coinbase.core` (Coinbase App's core:
different host, different credential, different signing scheme). Generic, auth-agnostic
building blocks (`RpcClient`/`RpcEndpoint`, `StreamClient`/`StreamEndpoint`, and the shared
`typed_core.exceptions` re-exports) live in `typed_coinbase.core` and are reused here rather
than duplicated — see `spec/core.md`.
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from ...core.endpoint.rpc import RpcClient
from ...core.endpoint.stream import StreamClient


@dataclass(kw_only=True, frozen=True)
class ExchangeBase:
  """Coinbase Exchange composition (design §5c): the resolved `core` for `exchange/`'s own
  composition -- `http` (the default forwarded field) and `streams` (the WebSocket Feed,
  one connection, public and private channels alike)."""

  client: RpcClient
  """REST transport."""
  feed_client: StreamClient
  """The WebSocket Feed connection."""

  @classmethod
  def new(cls, client: RpcClient, *, feed_client: StreamClient) -> Self:
    """Build from the already-resolved transports `CoinbaseBase.new` constructs.

    Args:
      client: REST transport.
      feed_client: Transport for the WebSocket Feed connection.
    """
    return cls(client=client, feed_client=feed_client)

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.client.__aenter__(), self.feed_client.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.client.__aexit__(exc_type, exc_value, traceback),
      self.feed_client.__aexit__(exc_type, exc_value, traceback),
    )
