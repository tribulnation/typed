from .accounts import Accounts
from .auto_compound import AutoCompound
from .positions import Positions
from .product_list import ProductList
from .subscribe import Subscribe


class DualInvestment(Accounts, AutoCompound, Positions, ProductList, Subscribe):
  """Binance dual_investment endpoints."""
