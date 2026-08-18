from dataclasses import dataclass, field
from coinbase.core.endpoint.stream import StreamEndpoint
from .futures_balance_summary import FuturesBalanceSummary
from .orders import Orders


@dataclass(frozen=True, kw_only=True)
class User(StreamEndpoint):
  """`user` endpoints."""

  futures_balance_summary: FuturesBalanceSummary = field(init=False)
  orders: Orders = field(init=False)

  def __post_init__(self):
    object.__setattr__(
      self, 'futures_balance_summary', FuturesBalanceSummary(client=self.client)
    )
    object.__setattr__(self, 'orders', Orders(client=self.client))
