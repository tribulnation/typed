from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint
from .orders import Orders


@dataclass(kw_only=True, frozen=True)
class SocialPay(RpcEndpoint):
  @cached_property
  def orders(self) -> Orders:
    return Orders(client=self.client)
