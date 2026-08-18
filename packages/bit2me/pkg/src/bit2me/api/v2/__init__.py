"""Hand-written PoC for the `v2` namespace. Stands in for the full generated tree
(account, currency, earn, loan, wallet) the codegen revamp will produce — only
`trading` is wired, for the same reason as `api/v1`.
"""

from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint

from .trading import V2Trading


@dataclass(kw_only=True, frozen=True)
class V2(RpcEndpoint):
  @cached_property
  def trading(self) -> V2Trading:
    return V2Trading(client=self.client)
