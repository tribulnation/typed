"""Coinbase App composition (design §5c): a hand-written `Base` holding the transports
`App`'s own children need, wrapped by the generated `App` composite.

`App` composes `accounts` and `advanced_trade.http` (both sharing one HTTP transport, the
default forwarded field) alongside `advanced_trade`'s own further WebSocket split -- so
`AppBase` also carries `market_client`/`user_client`, forwarded transitively into
`typed_coinbase.app.advanced_trade.core.AdvancedTradeBase` (design §5a: a `.new()`
parameter already satisfied by a same-named field on `self` forwards automatically, one
hop at a time)."""

from typing_extensions import Self
from dataclasses import dataclass
import asyncio

from ..core.endpoint.rpc import RpcClient
from ..core.endpoint.stream import StreamClient


@dataclass(kw_only=True, frozen=True)
class AppBase:
  """Coinbase App (Consumer APIs): the resolved `core` for `app/`'s own composition."""

  client: RpcClient
  """Shared HTTP transport for `accounts` and `advanced_trade.http`."""
  market_client: StreamClient
  """Advanced Trade's public WebSocket connection."""
  user_client: StreamClient
  """Advanced Trade's private WebSocket connection."""

  @classmethod
  def new(
    cls, client: RpcClient, *, market_client: StreamClient, user_client: StreamClient,
  ) -> Self:
    """Build from the already-resolved transports `CoinbaseBase.new` constructs.

    Args:
      client: Shared HTTP transport.
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
