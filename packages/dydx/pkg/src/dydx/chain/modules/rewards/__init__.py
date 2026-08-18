from .params import Params

from dydx.chain.core import GrpcEndpoint


class Rewards(
  Params,
  GrpcEndpoint,
):
  """Rewards endpoints."""
