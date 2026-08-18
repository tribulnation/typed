"""dYdX indexer client composition."""

from dataclasses import dataclass as _dataclass, field as _field
from types import TracebackType
from typing_extensions import Self, TypedDict
from .data import IndexerData, INDEXER_HTTP_URL, INDEXER_TESTNET_HTTP_URL
from .streams import IndexerStreams, INDEXER_WS_URL, INDEXER_TESTNET_WS_URL

class IndexerOptions(TypedDict, total=False):
  """Options for constructing dYdX indexer transports."""

  http_url: str
  """HTTP indexer base URL."""
  ws_url: str
  """WebSocket indexer URL."""
  validate: bool
  """Default response validation setting."""

@_dataclass
class Indexer:
  """Composed dYdX indexer client."""
  data: IndexerData = _field(default_factory=IndexerData)
  streams: IndexerStreams = _field(default_factory=IndexerStreams)

  @classmethod
  def new(cls, *, http_url: str = INDEXER_HTTP_URL, ws_url: str = INDEXER_WS_URL, validate: bool = True) -> Self:
    """Create a mainnet indexer client.
  
    Args:
      http_url: HTTP indexer base URL.
      ws_url: WebSocket indexer URL.
      validate: Override the client response validation default for this call.
  
    Returns:
      The configured indexer client.
    """
    return cls(
      data=IndexerData(url=http_url, default_validate=validate),
      streams=IndexerStreams.new(url=ws_url, validate=validate),
    )

  @classmethod
  def testnet(cls, *, http_url: str = INDEXER_TESTNET_HTTP_URL, ws_url: str = INDEXER_TESTNET_WS_URL, validate: bool = True) -> Self:
    """Create a testnet indexer client.
  
    Args:
      http_url: HTTP indexer base URL.
      ws_url: WebSocket indexer URL.
      validate: Override the client response validation default for this call.
  
    Returns:
      The configured indexer client.
    """
    return cls(
      data=IndexerData(url=http_url, default_validate=validate),
      streams=IndexerStreams.new(url=ws_url, validate=validate),
    )

  async def __aenter__(self) -> Self:
    """Enter the indexer client context.
  
    Returns:
      The configured indexer client.
    """
    await self.data.__aenter__()
    await self.streams.__aenter__()
    return self

  async def __aexit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None):
    """Exit the indexer client context."""
    await self.data.__aexit__(exc_type, exc_value, traceback)
    await self.streams.__aexit__(exc_type, exc_value, traceback)
