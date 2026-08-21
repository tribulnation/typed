from dataclasses import dataclass
from .all_tickers import AllTickersStream
from .candles import CandlesStream
from .deal import DealStream
from .depth import DepthStream
from .depth_full import DepthFullStream
from .fair_price import FairPriceStream
from .funding_rate import FundingRateStream
from .index_price import IndexPriceStream
from .ticker import TickerStream

@dataclass
class MarketStreams(
  AllTickersStream,
  CandlesStream,
  DealStream,
  DepthStream,
  DepthFullStream,
  FairPriceStream,
  FundingRateStream,
  IndexPriceStream,
  TickerStream,
):
  ...
