from .clob_pair import ClobPair
from .clob_pairs import ClobPairs
from .leverage import Leverage

from dydx.chain.core import GrpcEndpoint


class Clob(
  ClobPair,
  ClobPairs,
  Leverage,
  GrpcEndpoint,
):
  """Clob endpoints."""
