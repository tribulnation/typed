"""dYdX Indexer client base (design §2/§5/§5c, 2026-08-31 codegen mechanization).

`IndexerBase` is the resolved `core` for `indexer/`'s own composite position
(`codegen/config.toml` `[python.cores.indexer]`) -- a heterogeneous composite (design §5c) of
two children with genuinely different transports: `data` (HTTP) and `streams` (WS).
"""

from dataclasses import dataclass
from types import TracebackType

from typing_extensions import Self, TypedDict

from typed_dydx.indexer.data.core import INDEXER_HTTP_URL, INDEXER_TESTNET_HTTP_URL, IndexerHttpClient
from typed_dydx.indexer.streams.core import INDEXER_TESTNET_WS_URL, INDEXER_WS_URL, IndexerWsClient


class IndexerOptions(TypedDict, total=False):
  """Options for constructing dYdX indexer transports."""

  http_url: str
  """HTTP indexer base URL."""
  ws_url: str
  """WebSocket indexer URL."""
  validate: bool
  """Default response validation setting."""


@dataclass(kw_only=True, frozen=True)
class IndexerBase:
  """dYdX Indexer client base: one shared `IndexerHttpClient` (`data`) and one shared
  `IndexerWsClient` (`streams`)."""

  http_client: IndexerHttpClient
  ws_client: IndexerWsClient

  async def __aenter__(self) -> Self:
    """Open both shared transports for an async context."""
    await self.http_client.__aenter__()
    await self.ws_client.__aenter__()
    return self

  async def __aexit__(
    self,
    exc_type: type[BaseException] | None,
    exc: BaseException | None,
    traceback: TracebackType | None,
  ):
    """Close both shared transports for an async context."""
    await self.close()

  async def close(self):
    """Close both shared transports."""
    await self.http_client.__aexit__(None, None, None)
    await self.ws_client.__aexit__(None, None, None)

  @classmethod
  def new(
    cls, client: IndexerHttpClient, *, indexer_ws_client: IndexerWsClient,
  ) -> Self:
    """Build an Indexer core forwarding a root client's already-built transports
    (design §5a) -- not meant to be called directly; `client.indexer`'s generated
    `@cached_property` calls this, forwarding `DydxBase`'s own `indexer_http_client`/
    `indexer_ws_client` fields.

    Args:
      client: The HTTP transport (`DydxBase.indexer_http_client`, forwarded as this
        core's own `http_client`).
      indexer_ws_client: The WebSocket transport (`DydxBase.indexer_ws_client`).
    """
    return cls(http_client=client, ws_client=indexer_ws_client)

  @classmethod
  def mainnet(cls, *, http_url: str = INDEXER_HTTP_URL, ws_url: str = INDEXER_WS_URL, validate: bool = True) -> Self:
    """Create a mainnet Indexer client.

    Args:
      http_url: HTTP indexer base URL.
      ws_url: WebSocket indexer URL.
      validate: Default response validation setting.
    """
    return cls(
      http_client=IndexerHttpClient(url=http_url, validate=validate),
      ws_client=IndexerWsClient(url=ws_url, validate=validate),
    )

  @classmethod
  def testnet(
    cls, *, http_url: str = INDEXER_TESTNET_HTTP_URL, ws_url: str = INDEXER_TESTNET_WS_URL,
    validate: bool = True,
  ) -> Self:
    """Create a testnet Indexer client.

    Args:
      http_url: HTTP indexer base URL.
      ws_url: WebSocket indexer URL.
      validate: Default response validation setting.
    """
    return cls(
      http_client=IndexerHttpClient(url=http_url, validate=validate),
      ws_client=IndexerWsClient(url=ws_url, validate=validate),
    )
