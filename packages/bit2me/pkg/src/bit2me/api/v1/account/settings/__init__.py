from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint
from .two_factor import TwoFactor


@dataclass(kw_only=True, frozen=True)
class Settings(RpcEndpoint):
  @cached_property
  def two_factor(self) -> TwoFactor:
    return TwoFactor(client=self.client)
