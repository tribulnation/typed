"""The exchange surface: authenticated order/account-write actions, reachable over HTTP or
the shared WebSocket connection. Exposed as sibling transports on one constructed client
(`.http`, `.ws`), not a transport chosen once at construction that yields two disconnected
objects (`docs/production_standards.md` S23).
"""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from typed_core.http import HttpClient

from typed_hyperliquid.core.ws import SocketClient
from typed_hyperliquid.core.urls import ws_url as resolve_ws_url

from . import Exchange as ExchangeEndpoints
from .core import Wallet

__all__ = ['Exchange']


@dataclass(kw_only=True)
class Exchange:
  """Authenticated exchange client: order/account write actions, reachable over both HTTP
  and the shared WebSocket connection.

  Examples:
    ```python
    from typed_hyperliquid.exchange.main import Exchange

    exchange = Exchange.new(wallet)
    async with exchange:
      await exchange.http.order(...)
      await exchange.ws.cancel(...)
    ```
  """

  http: ExchangeEndpoints
  ws: ExchangeEndpoints

  @classmethod
  def new(
    cls,
    wallet: Wallet,
    *,
    mainnet: bool = True,
    validate: bool = True,
    http: HttpClient | None = None,
    ws: SocketClient | None = None,
    base_url: str | None = None,
    ws_url: str | None = None,
  ) -> Self:
    """Create an Exchange client reachable over both HTTP and WebSocket.

    Args:
      wallet: Private key or account object used to sign exchange actions.
      mainnet: Use mainnet when true, testnet when false.
      validate: Validate responses.
      http: Shared HTTP transport. A new one is created if omitted.
      ws: Shared WebSocket transport. A new one is created if omitted.
      base_url: Custom HTTP API root. If provided, takes precedence over
        `mainnet`.
      ws_url: Custom WebSocket URL. If provided, takes precedence over
        `mainnet`.
    """
    return cls(
      http=ExchangeEndpoints.http(
        wallet,
        mainnet=mainnet,
        validate=validate,
        http=http,
        base_url=base_url,
      ),
      ws=ExchangeEndpoints.ws_of(
        wallet,
        ws=ws or SocketClient(url=ws_url or resolve_ws_url(mainnet)),
        mainnet=mainnet,
        validate=validate,
      ),
    )

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.http.__aenter__(), self.ws.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http.__aexit__(exc_type, exc_value, traceback),
      self.ws.__aexit__(exc_type, exc_value, traceback),
    )
