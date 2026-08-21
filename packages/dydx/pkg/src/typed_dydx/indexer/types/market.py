"""dYdX indexer market types."""

from typing_extensions import Literal, TypedDict, NotRequired
from decimal import Decimal

MarketType = Literal['CROSS', 'ISOLATED']
MarketStatus = Literal['ACTIVE', 'PAUSED', 'CANCEL_ONLY', 'POST_ONLY', 'INITIALIZING', 'FINAL_SETTLEMENT']

class PerpetualMarket(TypedDict):
  """Perpetual market payload.

  References:
    - [dYdX API docs](https://docs.dydx.xyz/types/perpetual_market)
  """
  clobPairId: str
  ticker: str
  status: MarketStatus
  oraclePrice: NotRequired[Decimal|None]
  priceChange24H: Decimal
  volume24H: Decimal
  trades24H: int
  nextFundingRate: Decimal
  initialMarginFraction: Decimal
  maintenanceMarginFraction: Decimal
  openInterest: Decimal
  atomicResolution: int
  quantumConversionExponent: int
  tickSize: Decimal
  stepSize: Decimal
  stepBaseQuantums: int
  subticksPerTick: int
  marketType: MarketType
  openInterestLowerCap: NotRequired[Decimal|None]
  openInterestUpperCap: NotRequired[Decimal|None]
  baseOpenInterest: Decimal
  defaultFundingRate1H: NotRequired[Decimal|None]
