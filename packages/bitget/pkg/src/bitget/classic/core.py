"""Classic v2 REST root, composing one child per product domain — see `spec/core.md` Surfaces."""

from functools import cached_property

from ..core.endpoint.rpc import RpcEndpoint
from .public import Public
from .spot import Spot
from .mix import Mix
from .margin import Margin
from .copytrading import CopyTrading
from .convert import Convert
from .earn import Earn
from .tax import Tax
from .p2p import P2P
from .broker import Broker
from .user import User
from .institutional_loan import InstitutionalLoan


class Classic(RpcEndpoint):
  """Classic v2 REST surface, `/api/v2/...`, shared across all its product-domain children."""

  @cached_property
  def public(self) -> Public:
    return Public(client=self.client)

  @cached_property
  def spot(self) -> Spot:
    return Spot(client=self.client)

  @cached_property
  def mix(self) -> Mix:
    return Mix(client=self.client)

  @cached_property
  def margin(self) -> Margin:
    return Margin(client=self.client)

  @cached_property
  def copytrading(self) -> CopyTrading:
    return CopyTrading(client=self.client)

  @cached_property
  def convert(self) -> Convert:
    return Convert(client=self.client)

  @cached_property
  def earn(self) -> Earn:
    return Earn(client=self.client)

  @cached_property
  def tax(self) -> Tax:
    return Tax(client=self.client)

  @cached_property
  def p2p(self) -> P2P:
    return P2P(client=self.client)

  @cached_property
  def broker(self) -> Broker:
    return Broker(client=self.client)

  @cached_property
  def user(self) -> User:
    return User(client=self.client)

  @cached_property
  def institutional_loan(self) -> InstitutionalLoan:
    return InstitutionalLoan(client=self.client)
