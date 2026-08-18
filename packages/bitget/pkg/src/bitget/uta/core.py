"""UTA v3 REST root, composing one child per product domain — see `spec/core.md` Surfaces."""

from functools import cached_property

from ..core.endpoint.rpc import RpcEndpoint
from .market import Market
from .account import Account
from .trade import Trade
from .strategy import Strategy
from .position import Position
from .user import User
from .transfers import Transfers
from .loan import Loan
from .institutional_loan import InstitutionalLoan
from .copytrading import CopyTrading
from .broker import Broker
from .p2p import P2P
from .earn import Earn
from .tax import Tax


class Uta(RpcEndpoint):
  """UTA v3 REST surface, `/api/v3/...`, shared across all its product-domain children."""

  @cached_property
  def market(self) -> Market:
    return Market(client=self.client)

  @cached_property
  def account(self) -> Account:
    return Account(client=self.client)

  @cached_property
  def trade(self) -> Trade:
    return Trade(client=self.client)

  @cached_property
  def strategy(self) -> Strategy:
    return Strategy(client=self.client)

  @cached_property
  def position(self) -> Position:
    return Position(client=self.client)

  @cached_property
  def user(self) -> User:
    return User(client=self.client)

  @cached_property
  def transfers(self) -> Transfers:
    return Transfers(client=self.client)

  @cached_property
  def loan(self) -> Loan:
    return Loan(client=self.client)

  @cached_property
  def institutional_loan(self) -> InstitutionalLoan:
    return InstitutionalLoan(client=self.client)

  @cached_property
  def copytrading(self) -> CopyTrading:
    return CopyTrading(client=self.client)

  @cached_property
  def broker(self) -> Broker:
    return Broker(client=self.client)

  @cached_property
  def p2p(self) -> P2P:
    return P2P(client=self.client)

  @cached_property
  def earn(self) -> Earn:
    return Earn(client=self.client)

  @cached_property
  def tax(self) -> Tax:
    return Tax(client=self.client)
