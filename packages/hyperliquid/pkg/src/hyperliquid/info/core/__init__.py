"""Info endpoint base: RPC-shaped, unauthenticated, reachable over HTTP or the shared
WebSocket connection. See `spec/core.md` for the full surface writeup.
"""

from typing_extensions import Self
from dataclasses import dataclass
from datetime import timedelta

from typed_core.http import HttpClient

from hyperliquid.core.endpoint.rpc import RpcClient, RpcEndpoint
from hyperliquid.core.urls import http_base_url, ws_url as resolve_ws_url
from hyperliquid.core.ws import SocketClient
from .transport.http import InfoHttpClient
from .transport.ws import InfoSocketClient

InfoClient = RpcClient
"""Transport for Hyperliquid info requests -- same shape as the shared `RpcClient`."""


@dataclass(kw_only=True)
class InfoMixin(RpcEndpoint):
  """Base mixin for Hyperliquid info endpoint groups."""

  @classmethod
  def http(
    cls,
    *,
    mainnet: bool = True,
    validate: bool = True,
    http: HttpClient | None = None,
    base_url: str | None = None,
  ) -> Self:
    """Create an Info client with HTTP transport.

    Args:
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      http: Shared HTTP transport.
      base_url: Custom HTTP API root. If provided, takes
        precedence over `mainnet`.
    """
    client = InfoHttpClient(
      base_url=base_url or http_base_url(mainnet), http=http or HttpClient()
    )
    return cls(client=client, validate=validate)

  @classmethod
  def ws_of(cls, ws: SocketClient, *, validate: bool = True) -> Self:
    """Create an Info client from an existing WebSocket transport.

    Args:
      ws: Shared WebSocket transport.
      validate: Validate responses.
    """
    return cls(client=InfoSocketClient(ws=ws), validate=validate)

  @classmethod
  def ws(
    cls,
    *,
    mainnet: bool = True,
    validate: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    ws_url: str | None = None,
  ) -> Self:
    """Create an Info client with WebSocket transport.

    Args:
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      timeout: WebSocket request timeout.
      ws_url: Custom WebSocket URL. If provided, takes
        precedence over `mainnet`.
    """
    ws = SocketClient(url=ws_url or resolve_ws_url(mainnet), timeout=timeout)
    return cls.ws_of(ws, validate=validate)


__all__ = ['InfoClient', 'InfoMixin', 'InfoHttpClient', 'InfoSocketClient']
