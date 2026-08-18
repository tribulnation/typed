from dataclasses import dataclass
from .candles import Candles
from .deal import DealStream
from .depth import DepthStream
from .depth_full import DepthFull
from .fair_price import FairPriceStream
from .funding_rate import FundingRateStream
from .index_price import IndexPriceStream
from .ticker import TickerStream
from .tickers import Tickers

@dataclass
class MarketStreams(
  Candles,
  DealStream,
  DepthStream,
  DepthFull,
  FairPriceStream,
  FundingRateStream,
  IndexPriceStream,
  TickerStream,
  Tickers,
):
  ...
