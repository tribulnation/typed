from functools import cached_property

from binance.core.endpoint.rpc import RpcEndpoint
from .account import Account
from .locked import Locked


class OnChainYields(RpcEndpoint):
  """Binance on_chain_yields endpoints."""

  @cached_property
  def account(self) -> Account:
    return Account(client=self.client)

  @cached_property
  def locked(self) -> Locked:
    return Locked(client=self.client)
