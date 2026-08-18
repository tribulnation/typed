"""Hand-written PoC for the `v1` namespace. Stands in for the full generated tree
(account, currency, earn, loan, misc, signin, social_pay, teller, verifier, wallet,
blockchain_manager, b2m) the codegen revamp will produce — only `trading` is wired,
since the point of this PoC is proving the `http` surface's shape, not re-covering
ground the spec-authoring pass already covers per section.
"""

from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint

from .trading import V1Trading


@dataclass(kw_only=True, frozen=True)
class V1(RpcEndpoint):
  @cached_property
  def trading(self) -> V1Trading:
    return V1Trading(client=self.client)
