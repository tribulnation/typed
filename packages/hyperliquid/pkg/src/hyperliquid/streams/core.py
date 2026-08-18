"""Streams endpoint base: stream-shaped, WebSocket only, backed directly by the shared,
multiplexed `SocketClient` connection -- no `transport/` package here, unlike `info` and
`exchange`: `streams` has exactly one physical transport, so `SocketClient` (which already
satisfies `StreamClient` structurally) needs no adapter. See `spec/core.md` for the full
surface writeup.
"""

from typing_extensions import Self
from dataclasses import dataclass
from datetime import timedelta

from hyperliquid.core.endpoint.stream import StreamEndpoint
from hyperliquid.core.urls import ws_url as resolve_ws_url
from hyperliquid.core.ws import SocketClient


@dataclass(kw_only=True)
class StreamsMixin(StreamEndpoint):
  """Base mixin for Hyperliquid WebSocket stream endpoints."""

  @classmethod
  def of(cls, ws: SocketClient, *, validate: bool = True) -> Self:
    """Create a Streams client from an existing WebSocket transport.

    Args:
      ws: Shared WebSocket transport.
      validate: Validate stream messages.
    """
    return cls(client=ws, validate=validate)

  @classmethod
  def new(
    cls,
    *,
    mainnet: bool = True,
    timeout: timedelta = timedelta(seconds=10),
    validate: bool = True,
    ws_url: str | None = None,
  ) -> Self:
    """Create a Streams client with WebSocket transport.

    Args:
      mainnet: Use mainnet when true, testnet when false.
      timeout: WebSocket request timeout.
      validate: Validate stream messages.
      ws_url: Custom WebSocket URL. If provided, takes
        precedence over `mainnet`.
    """
    ws = SocketClient(url=ws_url or resolve_ws_url(mainnet), timeout=timeout)
    return cls.of(ws, validate=validate)
