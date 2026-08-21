from .collateral_pool_address import CollateralPoolAddress
from .subaccount import Subaccount
from .subaccounts import Subaccounts as _Subaccounts

from typed_dydx.chain.core import GrpcEndpoint


class Subaccounts(
  CollateralPoolAddress,
  Subaccount,
  _Subaccounts,
  GrpcEndpoint,
):
  """Subaccounts endpoints."""
