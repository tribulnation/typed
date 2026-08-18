from dataclasses import dataclass, field
from coinbase.core.endpoint.stream import StreamEndpoint
from .candles import Candles
from .heartbeats import Heartbeats
from .level2 import Level2
from .market_trades import MarketTrades
from .status import Status
from .ticker import Ticker
from .ticker_batch import TickerBatch


@dataclass(frozen=True, kw_only=True)
class MarketData(StreamEndpoint):
  """`market_data` endpoints."""

  candles: Candles = field(init=False)
  heartbeats: Heartbeats = field(init=False)
  level2: Level2 = field(init=False)
  market_trades: MarketTrades = field(init=False)
  status: Status = field(init=False)
  ticker: Ticker = field(init=False)
  ticker_batch: TickerBatch = field(init=False)

  def __post_init__(self):
    object.__setattr__(self, 'candles', Candles(client=self.client))
    object.__setattr__(self, 'heartbeats', Heartbeats(client=self.client))
    object.__setattr__(self, 'level2', Level2(client=self.client))
    object.__setattr__(self, 'market_trades', MarketTrades(client=self.client))
    object.__setattr__(self, 'status', Status(client=self.client))
    object.__setattr__(self, 'ticker', Ticker(client=self.client))
    object.__setattr__(self, 'ticker_batch', TickerBatch(client=self.client))
