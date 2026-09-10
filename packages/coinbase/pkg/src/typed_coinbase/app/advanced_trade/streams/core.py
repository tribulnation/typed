"""Advanced Trade WebSocket composition (design §5c): a hand-written `Base` holding the
two physical connections `Streams` composes -- public market data and the private `user`
channel -- wrapped by the generated `Streams` composite.

Unlike `AppBase`/`AdvancedTradeBase` (which forward a value through unchanged), this is the
bottom of the chain: both `market_data` and `user` resolve to the same leaf-capable
`app_streams` core (`typed_coinbase.core.endpoint.stream.StreamEndpoint`), so `router.json`'s
`children` mapping picks which field each one gets, and neither needs a `.new()` of its own
(design §3's plain default: `{child_class}(client=self.<forwarded_field>)`)."""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from ....core.endpoint.stream import StreamClient


@dataclass(kw_only=True, frozen=True)
class StreamsGroupBase:
  """Advanced Trade WebSocket, both connections: the resolved `core` for
  `app/advanced_trade/streams/`'s own composition."""

  market_client: StreamClient
  """Public channels (`wss://advanced-trade-ws.coinbase.com`)."""
  user_client: StreamClient
  """Private channels (`wss://advanced-trade-ws-user.coinbase.com`)."""

  @classmethod
  def new(cls, client: StreamClient, *, user_client: StreamClient) -> Self:
    """Build from the already-resolved transports `AdvancedTradeBase.new` constructs.

    Args:
      client: Transport for the public connection, forwarded as `market_client` --
        named `client` only to participate in design §5a's own-field-forwarding
        convention (`Generator._core_new_method` requires this exact name on every
        `.new()` this mechanism drives).
      user_client: Transport for the private connection.
    """
    return cls(market_client=client, user_client=user_client)

  async def __aenter__(self) -> Self:
    await asyncio.gather(self.market_client.__aenter__(), self.user_client.__aenter__())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await asyncio.gather(
      self.market_client.__aexit__(exc_type, exc_value, traceback),
      self.user_client.__aexit__(exc_type, exc_value, traceback),
    )
