from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint
from .balance import Balance
from .candles import Candles
from .funding_movements import FundingMovements
from .markets import Markets
from .orders import Orders
from .trades import Trades
from .wallets import Wallets
from .working_capital import WorkingCapital


@dataclass(kw_only=True, frozen=True)
class Trading(RpcEndpoint):
  @cached_property
  def balance(self) -> Balance:
    return Balance(client=self.client)

  @cached_property
  def candles(self) -> Candles:
    return Candles(client=self.client)

  @cached_property
  def funding_movements(self) -> FundingMovements:
    return FundingMovements(client=self.client)

  @cached_property
  def markets(self) -> Markets:
    return Markets(client=self.client)

  @cached_property
  def orders(self) -> Orders:
    return Orders(client=self.client)

  @cached_property
  def trades(self) -> Trades:
    return Trades(client=self.client)

  @cached_property
  def wallets(self) -> Wallets:
    return Wallets(client=self.client)

  @cached_property
  def working_capital(self) -> WorkingCapital:
    return WorkingCapital(client=self.client)
