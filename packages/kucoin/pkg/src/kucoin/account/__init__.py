"""KuCoin Account endpoints."""

from functools import cached_property

from .api_key_info import ApiKeyInfoEndpoint
from .cross_margin_account import CrossMarginAccountEndpoint
from .deposit import Deposit
from .futures_account import FuturesAccount
from .futures_ledgers import FuturesLedgers
from .hf_ledgers import HfLedgers
from .isolated_margin_account import IsolatedMarginAccountEndpoint
from .ledgers import Ledgers
from .margin_hf_ledgers import MarginHfLedgers
from .spot_account import SpotAccount
from .spot_account_type import SpotAccountType
from .spot_accounts import SpotAccounts
from .sub_account import SubAccount
from .sub_account_api import SubAccountApi
from .trade_fee import TradeFee
from .transfer import Transfer
from .user_info import UserInfo
from .withdrawals import Withdrawals


class Account(
  ApiKeyInfoEndpoint,
  CrossMarginAccountEndpoint,
  FuturesAccount,
  FuturesLedgers,
  HfLedgers,
  IsolatedMarginAccountEndpoint,
  Ledgers,
  MarginHfLedgers,
  SpotAccount,
  SpotAccountType,
  SpotAccounts,
  UserInfo,
):
  """KuCoin Account endpoints."""

  @cached_property
  def deposit(self) -> Deposit:
    """Deposit endpoints."""
    return Deposit(client=self.client)

  @cached_property
  def sub_account(self) -> SubAccount:
    """SubAccount endpoints."""
    return SubAccount(client=self.client)

  @cached_property
  def sub_account_api(self) -> SubAccountApi:
    """SubAccountApi endpoints."""
    return SubAccountApi(client=self.client)

  @cached_property
  def trade_fee(self) -> TradeFee:
    """TradeFee endpoints."""
    return TradeFee(client=self.client)

  @cached_property
  def transfer(self) -> Transfer:
    """Transfer endpoints."""
    return Transfer(client=self.client)

  @cached_property
  def withdrawals(self) -> Withdrawals:
    """Withdrawals endpoints."""
    return Withdrawals(client=self.client)
