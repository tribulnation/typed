from dataclasses import dataclass, field
from coinbase.core.endpoint.rpc import RpcEndpoint
from .accounts import Accounts
from .convert import Convert
from .fees import Fees
from .futures import Futures
from .key_permissions import KeyPermissions
from .orders import Orders
from .payment_methods import PaymentMethods
from .perpetuals import Perpetuals
from .portfolios import Portfolios
from .products import Products
from .server_time import ServerTimeEndpoint


@dataclass(frozen=True, kw_only=True)
class AdvancedTrade(RpcEndpoint):
  """`advanced_trade` endpoints."""

  accounts: Accounts = field(init=False)
  convert: Convert = field(init=False)
  fees: Fees = field(init=False)
  futures: Futures = field(init=False)
  key_permissions: KeyPermissions = field(init=False)
  orders: Orders = field(init=False)
  payment_methods: PaymentMethods = field(init=False)
  perpetuals: Perpetuals = field(init=False)
  portfolios: Portfolios = field(init=False)
  products: Products = field(init=False)
  server_time: ServerTimeEndpoint = field(init=False)

  def __post_init__(self):
    object.__setattr__(self, 'accounts', Accounts(client=self.client))
    object.__setattr__(self, 'convert', Convert(client=self.client))
    object.__setattr__(self, 'fees', Fees(client=self.client))
    object.__setattr__(self, 'futures', Futures(client=self.client))
    object.__setattr__(self, 'key_permissions', KeyPermissions(client=self.client))
    object.__setattr__(self, 'orders', Orders(client=self.client))
    object.__setattr__(self, 'payment_methods', PaymentMethods(client=self.client))
    object.__setattr__(self, 'perpetuals', Perpetuals(client=self.client))
    object.__setattr__(self, 'portfolios', Portfolios(client=self.client))
    object.__setattr__(self, 'products', Products(client=self.client))
    object.__setattr__(self, 'server_time', ServerTimeEndpoint(client=self.client))
