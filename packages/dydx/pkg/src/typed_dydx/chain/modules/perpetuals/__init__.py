from .liquidity_tiers import LiquidityTiers
from .perpetual import Perpetual
from .perpetuals import Perpetuals as _Perpetuals

from typed_dydx.chain.core import GrpcEndpoint


class Perpetuals(
  LiquidityTiers,
  Perpetual,
  _Perpetuals,
  GrpcEndpoint,
):
  """Perpetuals endpoints."""
