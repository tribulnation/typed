"""Default base URL of every Binance transport, and the per-product overrides
`Binance.new(urls=...)` accepts."""

from typing_extensions import TypedDict

SPOT_URL = 'https://api.binance.com'
USDM_FUTURES_URL = 'https://fapi.binance.com'
COINM_FUTURES_URL = 'https://dapi.binance.com'
OPTIONS_URL = 'https://eapi.binance.com'
PORTFOLIO_MARGIN_URL = 'https://papi.binance.com'
STREAM_URL = 'wss://stream.binance.com:9443/stream'
USDM_FUTURES_STREAM_URL = 'wss://fstream.binance.com/market/stream'
USDM_FUTURES_PUBLIC_STREAM_URL = 'wss://fstream.binance.com/public/stream'
COINM_FUTURES_STREAM_URL = 'wss://dstream.binance.com/stream'
OPTIONS_STREAM_URL = 'wss://nbstream.binance.com/eoptions/stream'
WS_API_URL = 'wss://ws-api.binance.com:443/ws-api/v3'
USDM_FUTURES_WS_API_URL = 'wss://ws-fapi.binance.com/ws-fapi/v1'
COINM_FUTURES_WS_API_URL = 'wss://ws-dapi.binance.com/ws-dapi/v1'
USDM_FUTURES_PRIVATE_STREAM_URL = 'wss://fstream.binance.com/private/ws'
COINM_FUTURES_PRIVATE_STREAM_URL = 'wss://dstream.binance.com/ws'
OPTIONS_PRIVATE_STREAM_URL = 'wss://fstream.binance.com/private/ws'
PORTFOLIO_MARGIN_PRIVATE_STREAM_URL = 'wss://fstream.binance.com/pm/ws'


class SpotUrls(TypedDict, total=False):
  """Spot URL overrides; a missing key keeps the default."""

  http: str
  """REST base URL (`SPOT_URL`)."""
  streams: str
  """Combined market-data stream URL (`STREAM_URL`)."""
  ws: str
  """WS API URL (`WS_API_URL`)."""


class UsdMFuturesUrls(TypedDict, total=False):
  """USDⓈ-M Futures URL overrides; a missing key keeps the default."""

  http: str
  """REST base URL (`USDM_FUTURES_URL`)."""
  streams: str
  """Combined market stream URL (`USDM_FUTURES_STREAM_URL`)."""
  public_streams: str
  """Combined public (book ticker, depth) stream URL (`USDM_FUTURES_PUBLIC_STREAM_URL`)."""
  private_streams: str
  """User-data stream base URL (`USDM_FUTURES_PRIVATE_STREAM_URL`)."""
  ws: str
  """WS API URL (`USDM_FUTURES_WS_API_URL`)."""


class CoinMFuturesUrls(TypedDict, total=False):
  """COIN-M Futures URL overrides; a missing key keeps the default."""

  http: str
  """REST base URL (`COINM_FUTURES_URL`)."""
  streams: str
  """Combined market stream URL (`COINM_FUTURES_STREAM_URL`)."""
  private_streams: str
  """User-data stream base URL (`COINM_FUTURES_PRIVATE_STREAM_URL`)."""
  ws: str
  """WS API URL (`COINM_FUTURES_WS_API_URL`)."""


class OptionsUrls(TypedDict, total=False):
  """Options URL overrides; a missing key keeps the default."""

  http: str
  """REST base URL (`OPTIONS_URL`)."""
  streams: str
  """Combined market stream URL (`OPTIONS_STREAM_URL`)."""
  private_streams: str
  """User-data stream base URL (`OPTIONS_PRIVATE_STREAM_URL`)."""


class PortfolioMarginUrls(TypedDict, total=False):
  """Portfolio Margin URL overrides; a missing key keeps the default."""

  http: str
  """REST base URL (`PORTFOLIO_MARGIN_URL`)."""
  private_streams: str
  """User-data stream base URL (`PORTFOLIO_MARGIN_PRIVATE_STREAM_URL`)."""


class Urls(TypedDict, total=False):
  """Base URL overrides, per product; a missing product or key keeps the default."""

  spot: SpotUrls
  usdm_futures: UsdMFuturesUrls
  coinm_futures: CoinMFuturesUrls
  options: OptionsUrls
  portfolio_margin: PortfolioMarginUrls
