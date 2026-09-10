"""Advanced Trade composition (design §5c): a hand-written `Base` holding the transports
`AdvancedTrade`'s own children need, wrapped by the generated `AdvancedTrade` composite.

`AdvancedTrade` composes `http` (the shared HTTP transport, the default forwarded field)
and `streams` (a further two-connection split) -- `streams` needs a `Base` of its own
(`typed_coinbase.app.advanced_trade.streams.core.StreamsGroupBase`), so this class forwards
both WebSocket transports down to it (design §5a, one hop at a time)."""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from ...core.endpoint.rpc import RpcClient
from ...core.endpoint.stream import StreamClient


@dataclass(kw_only=True, frozen=True)
class AdvancedTradeBase:
  """Advanced Trade (v3): the resolved `core` for `app/advanced_trade/`'s own composition."""

  client: RpcClient
  """REST transport -- orders, products, portfolios, fees, convert, futures/perpetuals."""
  market_client: StreamClient
  """Public WebSocket connection, forwarded down to `streams`."""
  user_client: StreamClient
  """Private WebSocket connection, forwarded down to `streams`."""

  @classmethod
  def new(
    cls, client: RpcClient, *, market_client: StreamClient, user_client: StreamClient,
  ) -> Self:
    """Build from the already-resolved transports `AppBase.new` constructs.

    Args:
      client: REST transport.
      market_client: Transport for the public WebSocket connection.
      user_client: Transport for the private WebSocket connection.
    """
    return cls(client=client, market_client=market_client, user_client=user_client)

  async def __aenter__(self) -> Self:
    await asyncio.gather(
      self.client.__aenter__(), self.market_client.__aenter__(), self.user_client.__aenter__(),
    )
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.client.__aexit__(exc_type, exc_value, traceback),
      self.market_client.__aexit__(exc_type, exc_value, traceback),
      self.user_client.__aexit__(exc_type, exc_value, traceback),
    )
