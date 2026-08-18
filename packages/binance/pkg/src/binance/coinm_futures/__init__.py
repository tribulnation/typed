from functools import cached_property

from binance.core.endpoint.rpc import RpcEndpoint
from .account import Account
from .market import Market
from .trading import Trading


class CoinMFutures(RpcEndpoint):
  """Binance coinm_futures endpoints."""

  @cached_property
  def account(self) -> Account:
    return Account(client=self.client)

  @cached_property
  def market(self) -> Market:
    return Market(client=self.client)

  @cached_property
  def trading(self) -> Trading:
    return Trading(client=self.client)
