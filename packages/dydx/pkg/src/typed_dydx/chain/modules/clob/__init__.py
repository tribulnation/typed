from .clob_pair import ClobPair
from .clob_pairs import ClobPairs
from .leverage import Leverage

from typed_dydx.chain.core import GrpcEndpoint


class Clob(
  ClobPair,
  ClobPairs,
  Leverage,
  GrpcEndpoint,
):
  """Clob endpoints."""
