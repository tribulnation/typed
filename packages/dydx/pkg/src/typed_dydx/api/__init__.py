from .data import Data
from .node import Node
from .streams import Streams

from typed_dydx.chain.core import GrpcEndpoint


class Api(
  Data,
  Node,
  Streams,
  GrpcEndpoint,
):
  """Api endpoints."""
