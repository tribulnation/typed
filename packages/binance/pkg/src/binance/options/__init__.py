from functools import cached_property

from binance.core.endpoint.rpc import RpcEndpoint
from .account import Account
from .block_trade import BlockTrade
from .market import Market
from .market_maker import MarketMaker
from .trading import Trading


class Options(RpcEndpoint):
  """Binance options endpoints."""

  @cached_property
  def account(self) -> Account:
    return Account(client=self.client)

  @cached_property
  def block_trade(self) -> BlockTrade:
    return BlockTrade(client=self.client)

  @cached_property
  def market(self) -> Market:
    return Market(client=self.client)

  @cached_property
  def market_maker(self) -> MarketMaker:
    return MarketMaker(client=self.client)

  @cached_property
  def trading(self) -> Trading:
    return Trading(client=self.client)
