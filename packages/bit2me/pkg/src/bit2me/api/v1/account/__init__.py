from dataclasses import dataclass
from functools import cached_property

from bit2me.core.endpoint import RpcEndpoint
from .addresses import Addresses
from .delete import Delete
from .deposit_estimations import DepositEstimations
from .employment_statuses import EmploymentStatuses
from .funds_origins import FundsOrigins
from .get import Get
from .identity_verification import IdentityVerification
from .person_identity import PersonIdentity
from .professions import Professions
from .purposes import Purposes
from .settings import Settings
from .subaccounts import Subaccounts
from .update import Update


@dataclass(kw_only=True, frozen=True)
class Account(RpcEndpoint):
  @cached_property
  def addresses(self) -> Addresses:
    return Addresses(client=self.client)

  @cached_property
  def delete(self) -> Delete:
    return Delete(client=self.client)

  @cached_property
  def deposit_estimations(self) -> DepositEstimations:
    return DepositEstimations(client=self.client)

  @cached_property
  def employment_statuses(self) -> EmploymentStatuses:
    return EmploymentStatuses(client=self.client)

  @cached_property
  def funds_origins(self) -> FundsOrigins:
    return FundsOrigins(client=self.client)

  @cached_property
  def get(self) -> Get:
    return Get(client=self.client)

  @cached_property
  def identity_verification(self) -> IdentityVerification:
    return IdentityVerification(client=self.client)

  @cached_property
  def person_identity(self) -> PersonIdentity:
    return PersonIdentity(client=self.client)

  @cached_property
  def professions(self) -> Professions:
    return Professions(client=self.client)

  @cached_property
  def purposes(self) -> Purposes:
    return Purposes(client=self.client)

  @cached_property
  def settings(self) -> Settings:
    return Settings(client=self.client)

  @cached_property
  def subaccounts(self) -> Subaccounts:
    return Subaccounts(client=self.client)

  @cached_property
  def update(self) -> Update:
    return Update(client=self.client)
