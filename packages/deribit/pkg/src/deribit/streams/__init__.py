"""Deribit's channel-subscription surface, reached through `Deribit.streams`.

Always WebSocket, on its own connection independent of `Deribit.ws`. `rpc` is an untyped
escape hatch reaching any JSON-RPC method over this same connection, for whatever isn't
covered by `Deribit.http`/`Deribit.ws`.
"""

from functools import cached_property
from dataclasses import dataclass

from ..core.endpoint.rpc import RpcEndpoint
from ..core.endpoint.stream import StreamEndpoint
from ..core.transport.ws import SocketRpcStreamClient
from .block_rfq import BlockRfq
from .market_data import MarketData
from .user import User


@dataclass(kw_only=True, frozen=True)
class Streams(StreamEndpoint):
  """Root of Deribit's WebSocket channel-subscription surface."""

  client: SocketRpcStreamClient
  """Narrowed from `StreamClient`: this surface is always WS-backed. Also implements
  `RpcClient`, which `rpc` below relies on."""

  @cached_property
  def rpc(self) -> RpcEndpoint:
    """Untyped escape hatch: any JSON-RPC method over this same connection."""
    return RpcEndpoint(client=self.client)

  @cached_property
  def market_data(self) -> MarketData:
    return MarketData(client=self.client)

  @cached_property
  def block_rfq(self) -> BlockRfq:
    return BlockRfq(client=self.client)

  @cached_property
  def user(self) -> User:
    return User(client=self.client)
