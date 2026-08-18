from functools import cached_property

from binance.core.endpoint.ws_rpc import WsRpcEndpoint
from .account import Account
from .general import General
from .trading import Trading
from .user_data import UserData


class CoinMFuturesWsApi(WsRpcEndpoint):
  """Binance coinm_futures_ws_api endpoints."""

  @cached_property
  def account(self) -> Account:
    return Account(client=self.client)

  @cached_property
  def general(self) -> General:
    return General(client=self.client)

  @cached_property
  def trading(self) -> Trading:
    return Trading(client=self.client)

  @cached_property
  def user_data(self) -> UserData:
    return UserData(client=self.client)
