from .market_param import MarketParam
from .market_price import MarketPrice
from .market_prices import MarketPrices

from typed_dydx.chain.core import GrpcEndpoint


class Prices(
  MarketParam,
  MarketPrice,
  MarketPrices,
  GrpcEndpoint,
):
  """Prices endpoints."""
