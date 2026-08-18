from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint
from .create import Create
from .list import List
from .two_factor import TwoFactor


@dataclass(kw_only=True, frozen=True)
class Subaccounts(RpcEndpoint):
  @cached_property
  def create(self) -> Create:
    return Create(client=self.client)

  @cached_property
  def list(self) -> List:
    return List(client=self.client)

  @cached_property
  def two_factor(self) -> TwoFactor:
    return TwoFactor(client=self.client)
