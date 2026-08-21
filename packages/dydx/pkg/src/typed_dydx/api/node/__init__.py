from .comet import Comet

from typed_dydx.chain.core import GrpcEndpoint


class Node(
  Comet,
  GrpcEndpoint,
):
  """Node endpoints."""
