from .announcements import Announcements
from .book import Book
from .book_grouped import BookGrouped
from .chart_trades import ChartTrades
from .estimated_expiration_price import EstimatedExpirationPrice
from .incremental_ticker import IncrementalTicker
from .instrument_creation import InstrumentCreation
from .instrument_state import InstrumentState
from .mark_price_options import MarkPriceOptions
from .perpetual import Perpetual
from .platform_state import PlatformState
from .platform_state_public_methods import PlatformStatePublicMethods
from .price_index import PriceIndex
from .price_ranking import PriceRanking
from .price_statistics import PriceStatistics
from .quote import Quote
from .ticker import TickerEndpoint
from .trades_by_instrument import TradesByInstrument
from .trades_by_kind_currency import TradesByKindCurrency
from .volatility_index import VolatilityIndex


class MarketData(
  Announcements,
  Book,
  BookGrouped,
  ChartTrades,
  EstimatedExpirationPrice,
  IncrementalTicker,
  InstrumentCreation,
  InstrumentState,
  MarkPriceOptions,
  Perpetual,
  PlatformState,
  PlatformStatePublicMethods,
  PriceIndex,
  PriceRanking,
  PriceStatistics,
  Quote,
  TickerEndpoint,
  TradesByInstrument,
  TradesByKindCurrency,
  VolatilityIndex,
):
  """MarketData endpoints."""
