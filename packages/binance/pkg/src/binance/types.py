from typing_extensions import Literal, TypedDict
from binance.core import Timestamp


class BnbBurnStatus(TypedDict):
  """Whether BNB Burn is enabled for Spot trading fees and Margin loan interest. Shared verbatim by `wallet.asset.bnb_burn.status` and `wallet.asset.bnb_burn.toggle`'s responses (swagger's `bnbBurnStatus` schema)."""

  spotBNBBurn: bool
  """Whether BNB is used to pay Spot trading fees."""
  interestBNBBurn: bool
  """Whether BNB is used to pay Margin loan interest."""


class BookTicker(TypedDict):
  """Best bid/ask price and quantity on the order book for one symbol."""

  symbol: str
  """Symbol."""
  bidPrice: str
  """Best bid price."""
  bidQty: str
  """Best bid quantity."""
  askPrice: str
  """Best ask price."""
  askQty: str
  """Best ask quantity."""


class MiniTickerEvent(TypedDict):
  """24hr rolling-window mini-ticker statistics for one symbol, as pushed on `<symbol>@miniTicker`. Shared verbatim by `streams.mini_ticker` (one object) and `streams.mini_ticker_all` (an array of these, one per changed symbol)."""

  e: Literal['24hrMiniTicker']
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  c: str
  """Close price."""
  o: str
  """Open price."""
  h: str
  """High price."""
  l: str
  """Low price."""
  v: str
  """Total traded base asset volume."""
  q: str
  """Total traded quote asset volume."""


OrderBookLevel = tuple[str, str]


SpotCandle = tuple[
  Timestamp, str, str, str, str, str, Timestamp, str, int, str, str, str
]


class SpotTrade(TypedDict):
  """One executed trade. Shared verbatim by `recentTrades` and `historicalTrades`, whose upstream response examples are byte-identical."""

  id: int
  """Trade ID."""
  price: str
  """Trade price."""
  qty: str
  """Trade quantity, in the base asset."""
  quoteQty: str
  """Trade quantity, in the quote asset."""
  time: Timestamp
  """Trade time."""
  isBuyerMaker: bool
  """Whether the buyer was the maker."""
  isBestMatch: bool
  """Whether the trade was the best price match."""


class SymbolPrice(TypedDict):
  """Latest price for one symbol."""

  symbol: str
  """Symbol."""
  price: str
  """Latest price."""


class Ticker24hrFull(TypedDict):
  """24hr rolling window price change statistics for one symbol, `type=FULL` (the default)."""

  symbol: str
  """Symbol."""
  priceChange: str
  """Absolute price change over the window."""
  priceChangePercent: str
  """Relative price change over the window, in percent."""
  weightedAvgPrice: str
  """Quote volume divided by base volume over the window."""
  prevClosePrice: str
  """Close price of the previous window."""
  lastPrice: str
  """Latest price."""
  lastQty: str
  """Latest trade quantity."""
  bidPrice: str
  """Best bid price."""
  bidQty: str
  """Best bid quantity."""
  askPrice: str
  """Best ask price."""
  askQty: str
  """Best ask quantity."""
  openPrice: str
  """Opening price of the window."""
  highPrice: str
  """Highest price in the window."""
  lowPrice: str
  """Lowest price in the window."""
  volume: str
  """Total trade volume, in the base asset."""
  quoteVolume: str
  """Total trade volume, in the quote asset."""
  openTime: Timestamp
  """Start of the ticker window."""
  closeTime: Timestamp
  """End of the ticker window."""
  firstId: int
  """First trade ID considered."""
  lastId: int
  """Last trade ID considered."""
  count: int
  """Number of trades in the window."""


class Ticker24hrMini(TypedDict):
  """24hr rolling window price change statistics for one symbol, `type=MINI`."""

  symbol: str
  """Symbol."""
  openPrice: str
  """Opening price of the window."""
  highPrice: str
  """Highest price in the window."""
  lowPrice: str
  """Lowest price in the window."""
  lastPrice: str
  """Closing price of the window."""
  volume: str
  """Total trade volume, in the base asset."""
  quoteVolume: str
  """Total trade volume, in the quote asset."""
  openTime: Timestamp
  """Start of the ticker window."""
  closeTime: Timestamp
  """End of the ticker window."""
  firstId: int
  """First trade ID considered."""
  lastId: int
  """Last trade ID considered."""
  count: int
  """Total trade count."""


class TickerEvent(TypedDict):
  """24hr rolling-window ticker statistics for one symbol, as pushed on `<symbol>@ticker` -- backs `Streams.ticker()`. Confirmed live during this pass's core-wiring smoke test. Distinct from the REST `Ticker24hrFull`/`Ticker24hrMini` schemas -- the wire push uses Binance's abbreviated single-letter field names, not the REST response's spelled-out ones."""

  e: Literal['24hrTicker']
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  p: str
  """Absolute price change over the window."""
  P: str
  """Relative price change over the window, in percent."""
  w: str
  """Weighted average price."""
  x: str
  """First trade price before the 24hr rolling window."""
  c: str
  """Last price."""
  Q: str
  """Last quantity."""
  b: str
  """Best bid price."""
  B: str
  """Best bid quantity."""
  a: str
  """Best ask price."""
  A: str
  """Best ask quantity."""
  o: str
  """Open price."""
  h: str
  """High price."""
  l: str
  """Low price."""
  v: str
  """Total traded base asset volume."""
  q: str
  """Total traded quote asset volume."""
  O: Timestamp
  """Statistics open time."""
  C: Timestamp
  """Statistics close time."""
  F: int
  """First trade ID."""
  L: int
  """Last trade ID."""
  n: int
  """Total number of trades."""


class TickerTradingDayFull(TypedDict):
  """Price change statistics for one symbol over a trading day, `type=FULL` (the default)."""

  symbol: str
  """Symbol."""
  priceChange: str
  """Absolute price change over the trading day."""
  priceChangePercent: str
  """Relative price change over the trading day, in percent."""
  weightedAvgPrice: str
  """Quote volume divided by base volume over the trading day."""
  openPrice: str
  """Opening price of the trading day."""
  highPrice: str
  """Highest price in the trading day."""
  lowPrice: str
  """Lowest price in the trading day."""
  lastPrice: str
  """Latest price."""
  volume: str
  """Volume, in the base asset."""
  quoteVolume: str
  """Sum of (price * volume) for all trades in the trading day."""
  openTime: Timestamp
  """Start of the trading day, per the request's `timeZone`."""
  closeTime: Timestamp
  """End of the trading day, per the request's `timeZone`."""
  firstId: int
  """Trade ID of the first trade in the trading day."""
  lastId: int
  """Trade ID of the last trade in the trading day."""
  count: int
  """Number of trades in the trading day."""


class TickerTradingDayMini(TypedDict):
  """Price change statistics for one symbol over a trading day, `type=MINI`."""

  symbol: str
  """Symbol."""
  openPrice: str
  """Opening price of the trading day."""
  highPrice: str
  """Highest price in the trading day."""
  lowPrice: str
  """Lowest price in the trading day."""
  lastPrice: str
  """Latest price."""
  volume: str
  """Volume, in the base asset."""
  quoteVolume: str
  """Sum of (price * volume) for all trades in the trading day."""
  openTime: Timestamp
  """Start of the trading day, per the request's `timeZone`."""
  closeTime: Timestamp
  """End of the trading day, per the request's `timeZone`."""
  firstId: int
  """Trade ID of the first trade in the trading day."""
  lastId: int
  """Trade ID of the last trade in the trading day."""
  count: int
  """Number of trades in the trading day."""


class TickerWindowEvent(TypedDict):
  """Rolling-window ticker statistics for one symbol over a caller-chosen window size, as pushed on `<symbol>@ticker_<window>`. Shared verbatim by `streams.ticker_window` (one object) and `streams.ticker_window_all` (an array of these, one per changed symbol). Distinct from the REST `TickerWindowFull`/`TickerWindowMini` schemas -- the wire push uses Binance's abbreviated single-letter field names, not the REST response's spelled-out ones."""

  e: str
  """Event type, e.g. `1hTicker`, `4hTicker`, `1dTicker` -- matches the subscribed window size."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  p: str
  """Absolute price change over the window."""
  P: str
  """Relative price change over the window, in percent."""
  o: str
  """Open price."""
  h: str
  """High price."""
  l: str
  """Low price."""
  c: str
  """Last price."""
  w: str
  """Weighted average price."""
  v: str
  """Total traded base asset volume."""
  q: str
  """Total traded quote asset volume."""
  O: Timestamp
  """Statistics open time. Always starts on a minute boundary."""
  C: Timestamp
  """Statistics close time -- the current time of the update, so the effective window may be up to 59999ms wider than the subscribed window size."""
  F: int
  """First trade ID considered."""
  L: int
  """Last trade ID considered."""
  n: int
  """Total number of trades."""


class TickerWindowFull(TypedDict):
  """Price change statistics for one symbol over a caller-chosen rolling window, `type=FULL` (the default)."""

  symbol: str
  """Symbol."""
  priceChange: str
  """Absolute price change over the window."""
  priceChangePercent: str
  """Relative price change over the window, in percent."""
  weightedAvgPrice: str
  """Quote volume divided by base volume over the window."""
  openPrice: str
  """Opening price of the window."""
  highPrice: str
  """Highest price in the window."""
  lowPrice: str
  """Lowest price in the window."""
  lastPrice: str
  """Latest price."""
  volume: str
  """Volume, in the base asset."""
  quoteVolume: str
  """Sum of (price * volume) for all trades in the window."""
  openTime: Timestamp
  """Open time for the ticker window."""
  closeTime: Timestamp
  """Close time for the ticker window; the current time of the request."""
  firstId: int
  """First trade ID in the window."""
  lastId: int
  """Last trade ID in the window."""
  count: int
  """Number of trades in the window."""


class TickerWindowMini(TypedDict):
  """Price change statistics for one symbol over a caller-chosen rolling window, `type=MINI`."""

  symbol: str
  """Symbol."""
  openPrice: str
  """Opening price of the window."""
  highPrice: str
  """Highest price in the window."""
  lowPrice: str
  """Lowest price in the window."""
  lastPrice: str
  """Latest price."""
  volume: str
  """Volume, in the base asset."""
  quoteVolume: str
  """Sum of (price * volume) for all trades in the window."""
  openTime: Timestamp
  """Open time for the ticker window."""
  closeTime: Timestamp
  """Close time for the ticker window; the current time of the request."""
  firstId: int
  """First trade ID in the window."""
  lastId: int
  """Last trade ID in the window."""
  count: int
  """Number of trades in the window."""


UniversalTransferType = Literal[
  'MAIN_UMFUTURE',
  'MAIN_CMFUTURE',
  'MAIN_MARGIN',
  'UMFUTURE_MAIN',
  'UMFUTURE_MARGIN',
  'CMFUTURE_MAIN',
  'CMFUTURE_MARGIN',
  'MARGIN_MAIN',
  'MARGIN_UMFUTURE',
  'MARGIN_CMFUTURE',
  'ISOLATEDMARGIN_MARGIN',
  'MARGIN_ISOLATEDMARGIN',
  'ISOLATEDMARGIN_ISOLATEDMARGIN',
  'MAIN_FUNDING',
  'FUNDING_MAIN',
  'FUNDING_UMFUTURE',
  'UMFUTURE_FUNDING',
  'MARGIN_FUNDING',
  'FUNDING_MARGIN',
  'FUNDING_CMFUTURE',
  'CMFUTURE_FUNDING',
  'MAIN_OPTION',
  'OPTION_MAIN',
  'UMFUTURE_OPTION',
  'OPTION_UMFUTURE',
  'MARGIN_OPTION',
  'OPTION_MARGIN',
  'FUNDING_OPTION',
  'OPTION_FUNDING',
  'MAIN_PORTFOLIO_MARGIN',
  'PORTFOLIO_MARGIN_MAIN',
]
