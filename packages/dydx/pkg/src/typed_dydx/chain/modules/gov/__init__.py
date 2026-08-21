from .proposals import Proposals

from typed_dydx.chain.core import GrpcEndpoint


class Gov(
  Proposals,
  GrpcEndpoint,
):
  """Gov endpoints."""
