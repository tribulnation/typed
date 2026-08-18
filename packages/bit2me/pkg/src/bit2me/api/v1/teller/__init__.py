from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint
from .ibans import Ibans
from .orders import Orders
from .pockets import Pockets


@dataclass(kw_only=True, frozen=True)
class Teller(RpcEndpoint):
  @cached_property
  def ibans(self) -> Ibans:
    return Ibans(client=self.client)

  @cached_property
  def orders(self) -> Orders:
    return Orders(client=self.client)

  @cached_property
  def pockets(self) -> Pockets:
    return Pockets(client=self.client)
