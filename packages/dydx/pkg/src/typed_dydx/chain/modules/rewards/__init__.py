from .params import Params

from typed_dydx.chain.core import GrpcEndpoint


class Rewards(
  Params,
  GrpcEndpoint,
):
  """Rewards endpoints."""
