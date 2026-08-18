from .candles import Candles
from .contract_info import ContractInfo
from .deals import Deals
from .depth import Depth
from .depth_commits import DepthCommits
from .fair_price import FairPrice
from .fair_price_candles import FairPriceCandles
from .funding_rate import FundingRate
from .funding_rate_history import FundingRateHistory
from .index_price import IndexPrice
from .index_price_candles import IndexPriceCandles
from .ping import Ping
from .risk_reverse import RiskReverse
from .risk_reverse_history import RiskReverseHistory
from .support_currencies import SupportCurrencies
from .ticker import Ticker

class Market(Candles, ContractInfo, Deals, Depth, DepthCommits, FairPrice, FairPriceCandles, FundingRate, FundingRateHistory, IndexPrice, IndexPriceCandles, Ping, RiskReverse, RiskReverseHistory, SupportCurrencies, Ticker):
  ...
