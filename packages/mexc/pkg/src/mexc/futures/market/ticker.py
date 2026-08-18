from typing_extensions import NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.futures.core import FuturesMixin

class ContractTickerListItem(TypedDict):
  """Contract ticker/trend data."""
  symbol: str
  """Contract symbol."""
  lastPrice: float
  """Latest traded price."""
  bid1: NotRequired[float]
  """Best bid price."""
  ask1: NotRequired[float]
  """Best ask price."""
  volume24: NotRequired[float]
  """24-hour contract volume."""
  amount24: NotRequired[float]
  """24-hour quote amount."""
  holdVol: NotRequired[float]
  """Open interest volume."""
  lower24Price: NotRequired[float]
  """24-hour low price."""
  high24Price: NotRequired[float]
  """24-hour high price."""
  riseFallRate: NotRequired[float]
  """Rise/fall rate."""
  riseFallValue: NotRequired[float]
  """Rise/fall value."""
  indexPrice: NotRequired[float]
  """Index price."""
  fairPrice: NotRequired[float]
  """Fair price."""
  fundingRate: NotRequired[float]
  """Funding rate."""
  timestamp: Timestamp
  """Ticker timestamp in milliseconds."""

class RiseFallRates(TypedDict):
  """Returned riseFallRates field."""
  r: float
  """Returned r field."""
  r180: float
  """Returned r180 field."""
  r30: float
  """Returned r30 field."""
  r365: float
  """Returned r365 field."""
  r7: float
  """Returned r7 field."""
  r90: float
  """Returned r90 field."""
  v: float
  """Returned v field."""
  zone: str
  """Returned zone field."""

class ContractTicker(TypedDict):
  """Contract ticker/trend data."""
  symbol: str
  """Contract symbol."""
  lastPrice: float
  """Latest traded price."""
  bid1: float
  """Best bid price."""
  ask1: float
  """Best ask price."""
  volume24: float
  """24-hour contract volume."""
  amount24: float
  """24-hour quote amount."""
  holdVol: float
  """Open interest volume."""
  lower24Price: float
  """24-hour low price."""
  high24Price: float
  """24-hour high price."""
  riseFallRate: float
  """Rise/fall rate."""
  riseFallValue: float
  """Rise/fall value."""
  indexPrice: float
  """Index price."""
  fairPrice: float
  """Fair price."""
  fundingRate: float
  """Funding rate."""
  timestamp: Timestamp
  """Ticker timestamp in milliseconds."""
  contractId: int
  """contractId identifier."""
  maxBidPrice: float
  """Returned maxBidPrice field."""
  minAskPrice: float
  """Returned minAskPrice field."""
  riseFallRates: RiseFallRates
  riseFallRatesOfTimezone: list[float]
  """Rise/fall rates for configured timezone windows."""

class TickerResponse(TypedDict):
  """Ticker envelope"""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[ContractTicker | list[ContractTickerListItem]]
  """Ticker object when symbol is supplied, otherwise a list."""

adapter = validator(TickerResponse)

class Ticker(FuturesMixin):
  async def ticker(
    self, *,
    symbol: str | None = None, validate: bool | None = None,
  ) -> TickerResponse:
    """Return ticker/trend data, optionally filtered to one futures contract.

    Args:
      symbol: Optional contract symbol filter, for example BTC_USDT.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-contract-trend-data)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    r = await self.request('GET', '/api/v1/contract/ticker', params=params)
    return self.envelope_output(r.text, adapter, validate)
