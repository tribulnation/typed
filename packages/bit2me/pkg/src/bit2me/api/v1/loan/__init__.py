from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint
from .ltv import Ltv
from .movements import Movements
from .orders import Orders


@dataclass(kw_only=True, frozen=True)
class Loan(RpcEndpoint):
  @cached_property
  def ltv(self) -> Ltv:
    return Ltv(client=self.client)

  @cached_property
  def movements(self) -> Movements:
    return Movements(client=self.client)

  @cached_property
  def orders(self) -> Orders:
    return Orders(client=self.client)
