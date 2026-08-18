from .comet import Comet

from dydx.chain.core import GrpcEndpoint


class Node(
  Comet,
  GrpcEndpoint,
):
  """Node endpoints."""
