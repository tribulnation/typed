from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint
from .account import Account
from .currency import Currency
from .earn import Earn
from .loan import Loan
from .trading import Trading
from .wallet import Wallet


@dataclass(kw_only=True, frozen=True)
class V2(RpcEndpoint):
  @cached_property
  def account(self) -> Account:
    return Account(client=self.client)

  @cached_property
  def currency(self) -> Currency:
    return Currency(client=self.client)

  @cached_property
  def earn(self) -> Earn:
    return Earn(client=self.client)

  @cached_property
  def loan(self) -> Loan:
    return Loan(client=self.client)

  @cached_property
  def trading(self) -> Trading:
    return Trading(client=self.client)

  @cached_property
  def wallet(self) -> Wallet:
    return Wallet(client=self.client)
