from functools import cached_property

from .address_book import AddressBook
from .beneficiary import Beneficiary
from .deposits import Deposits
from .rewards import Rewards
from .transfers import Transfers
from .withdrawals import Withdrawals

from deribit.core import RpcEndpoint


class Wallet(RpcEndpoint):
  """Wallet endpoints."""

  @cached_property
  def address_book(self) -> AddressBook:
    return AddressBook(client=self.client)

  @cached_property
  def beneficiary(self) -> Beneficiary:
    return Beneficiary(client=self.client)

  @cached_property
  def deposits(self) -> Deposits:
    return Deposits(client=self.client)

  @cached_property
  def rewards(self) -> Rewards:
    return Rewards(client=self.client)

  @cached_property
  def transfers(self) -> Transfers:
    return Transfers(client=self.client)

  @cached_property
  def withdrawals(self) -> Withdrawals:
    return Withdrawals(client=self.client)
