"""Advanced Trade (v3): REST and both WebSocket connections, composed as one group."""

from dataclasses import dataclass
import asyncio

from typed_coinbase.core.endpoint.rpc import RpcClient
from typed_coinbase.core.endpoint.stream import StreamClient
from .http import Http as AdvancedTradeHttp
from .streams import Streams


@dataclass(kw_only=True)
class AdvancedTrade:
  """Advanced Trade (v3): orders, products, portfolios, fees, convert, and both
  WebSocket connections.

  References:
    - [Advanced Trade overview](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/overview)
  """

  http: AdvancedTradeHttp
  """REST — orders, products, portfolios, fees, convert.

  References:
    - [Advanced Trade REST Endpoints](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/rest-api)
  """
  streams: Streams
  """Both WebSocket connections.

  References:
    - [Advanced Trade WebSocket Endpoints](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-endpoints)
  """

  @classmethod
  def new(
    cls,
    *,
    http: RpcClient,
    market_data: StreamClient,
    user: StreamClient,
  ) -> 'AdvancedTrade':
    """Build the REST client and both WebSocket connections from their own
    already-resolved transports.

    Args:
      http: Transport for the REST surface.
      market_data: Transport for the public WebSocket connection.
      user: Transport for the private WebSocket connection.
    """
    return cls(
      http=AdvancedTradeHttp.new(client=http),
      streams=Streams.new(market_data=market_data, user=user),
    )

  async def __aenter__(self) -> 'AdvancedTrade':
    await asyncio.gather(self.http.__aenter__(), self.streams.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.http.__aexit__(exc_type, exc_value, traceback),
      self.streams.__aexit__(exc_type, exc_value, traceback),
    )
