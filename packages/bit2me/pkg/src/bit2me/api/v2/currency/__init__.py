from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint
from .assets import Assets


@dataclass(kw_only=True, frozen=True)
class Currency(RpcEndpoint):
  @cached_property
  def assets(self) -> Assets:
    return Assets(client=self.client)
