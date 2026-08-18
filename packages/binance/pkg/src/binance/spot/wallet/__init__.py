from functools import cached_property

from binance.core.endpoint.rpc import RpcEndpoint
from .account import Account
from .asset import Asset
from .capital import Capital
from .local_entity import LocalEntity
from .others import Others


class Wallet(RpcEndpoint):
  """Binance wallet endpoints."""

  @cached_property
  def account(self) -> Account:
    return Account(client=self.client)

  @cached_property
  def asset(self) -> Asset:
    return Asset(client=self.client)

  @cached_property
  def capital(self) -> Capital:
    return Capital(client=self.client)

  @cached_property
  def local_entity(self) -> LocalEntity:
    return LocalEntity(client=self.client)

  @cached_property
  def others(self) -> Others:
    return Others(client=self.client)
