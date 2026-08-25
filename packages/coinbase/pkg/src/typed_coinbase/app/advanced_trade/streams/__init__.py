"""Advanced Trade WebSocket: two separate physical connections, composed as one group."""

from dataclasses import dataclass
import asyncio

from typed_coinbase.core.endpoint.stream import StreamClient
from .market_data import MarketData
from .user import User


@dataclass(kw_only=True)
class Streams:
  """Advanced Trade WebSocket, both connections.

  References:
    - [Advanced Trade WebSocket Endpoints](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-endpoints)
  """

  market_data: MarketData
  """Public channels (`wss://advanced-trade-ws.coinbase.com`).

  References:
    - [Advanced Trade WebSocket overview](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-overview)
  """
  user: User
  """Private channels (`wss://advanced-trade-ws-user.coinbase.com`).

  References:
    - [Advanced Trade WebSocket overview](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-overview)
  """

  @classmethod
  def new(cls, *, market_data: StreamClient, user: StreamClient) -> 'Streams':
    """Build both connections from their own already-resolved clients.

    Args:
      market_data: Transport for the public connection.
      user: Transport for the private connection.
    """
    return cls(
      market_data=MarketData.new(client=market_data),
      user=User.new(client=user),
    )

  async def __aenter__(self) -> 'Streams':
    await asyncio.gather(self.market_data.__aenter__(), self.user.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.market_data.__aexit__(exc_type, exc_value, traceback),
      self.user.__aexit__(exc_type, exc_value, traceback),
    )
