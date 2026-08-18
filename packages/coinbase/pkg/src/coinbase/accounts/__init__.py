from dataclasses import dataclass, field
from coinbase.core.endpoint.rpc import RpcEndpoint
from .addresses import Addresses
from .currencies import Currencies
from .deposits import Deposits
from .exchange_rates import ExchangeRates
from .get import Get
from .list import List
from .prices import Prices
from .subscriptions import Subscriptions
from .time import Time
from .transactions import Transactions
from .withdrawals import Withdrawals


@dataclass(frozen=True, kw_only=True)
class Accounts(RpcEndpoint):
  """`accounts` endpoints."""

  addresses: Addresses = field(init=False)
  currencies: Currencies = field(init=False)
  deposits: Deposits = field(init=False)
  exchange_rates: ExchangeRates = field(init=False)
  get: Get = field(init=False)
  list: List = field(init=False)
  prices: Prices = field(init=False)
  subscriptions: Subscriptions = field(init=False)
  time: Time = field(init=False)
  transactions: Transactions = field(init=False)
  withdrawals: Withdrawals = field(init=False)

  def __post_init__(self):
    object.__setattr__(self, 'addresses', Addresses(client=self.client))
    object.__setattr__(self, 'currencies', Currencies(client=self.client))
    object.__setattr__(self, 'deposits', Deposits(client=self.client))
    object.__setattr__(self, 'exchange_rates', ExchangeRates(client=self.client))
    object.__setattr__(self, 'get', Get(client=self.client))
    object.__setattr__(self, 'list', List(client=self.client))
    object.__setattr__(self, 'prices', Prices(client=self.client))
    object.__setattr__(self, 'subscriptions', Subscriptions(client=self.client))
    object.__setattr__(self, 'time', Time(client=self.client))
    object.__setattr__(self, 'transactions', Transactions(client=self.client))
    object.__setattr__(self, 'withdrawals', Withdrawals(client=self.client))
