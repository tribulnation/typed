from functools import cached_property

from binance.core.endpoint.rpc import RpcEndpoint
from .futures import Futures
from .spot import Spot


class Algo(RpcEndpoint):
  """Binance algo endpoints."""

  @cached_property
  def futures(self) -> Futures:
    return Futures(client=self.client)

  @cached_property
  def spot(self) -> Spot:
    return Spot(client=self.client)
