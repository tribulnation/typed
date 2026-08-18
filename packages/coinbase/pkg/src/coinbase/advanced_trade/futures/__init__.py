from dataclasses import dataclass, field
from coinbase.core.endpoint.rpc import RpcEndpoint
from .balance_summary import BalanceSummary
from .intraday_margin import IntradayMargin
from .positions import Positions
from .sweeps import Sweeps


@dataclass(frozen=True, kw_only=True)
class Futures(RpcEndpoint):
  """`futures` endpoints."""

  balance_summary: BalanceSummary = field(init=False)
  intraday_margin: IntradayMargin = field(init=False)
  positions: Positions = field(init=False)
  sweeps: Sweeps = field(init=False)

  def __post_init__(self):
    object.__setattr__(self, 'balance_summary', BalanceSummary(client=self.client))
    object.__setattr__(self, 'intraday_margin', IntradayMargin(client=self.client))
    object.__setattr__(self, 'positions', Positions(client=self.client))
    object.__setattr__(self, 'sweeps', Sweeps(client=self.client))
