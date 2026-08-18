from .proposals import Proposals

from dydx.chain.core import GrpcEndpoint


class Gov(
  Proposals,
  GrpcEndpoint,
):
  """Gov endpoints."""
