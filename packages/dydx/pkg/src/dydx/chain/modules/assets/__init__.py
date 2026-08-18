from .asset import Asset
from .assets import Assets as _Assets

from dydx.chain.core import GrpcEndpoint


class Assets(
  Asset,
  _Assets,
  GrpcEndpoint,
):
  """Assets endpoints."""
