"""`GET /api/v2/symbols/{symbol}` — Get Symbol."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class SpotSymbolDetail(TypedDict):
  """Order-placement configuration for one trading pair."""

  symbol: str
  """Trading pair identifier, e.g. `BTC-USDT`."""
  name: str
  """Display name (usually equal to `symbol`)."""
  baseCurrency: str
  """Base asset."""
  quoteCurrency: str
  """Quote asset."""
  feeCurrency: str
  """Currency trading fees on this pair are charged in."""
  market: str
  """Market category this pair is grouped under (see `spot.market_list` for the live set of categories — not a fixed enum, categories are reorganized over time)."""
  baseMinSize: str
  """Minimum order size, in base currency."""
  baseMaxSize: str
  """Maximum order size, in base currency."""
  quoteMinSize: str
  """Minimum order value, in quote currency."""
  quoteMaxSize: str
  """Maximum order value, in quote currency."""
  baseIncrement: str
  """Base currency amount step."""
  quoteIncrement: str
  """Quote currency amount step."""
  priceIncrement: str
  """Minimum order price and its step."""
  priceLimitRate: str
  """Max fraction an order's price may deviate from the last price. Undocumented on this page but present live — see All Symbols, where it is documented."""
  minFunds: str | None
  """Minimum order value required to place an order, or `null` when the pair enforces none. Undocumented as nullable on this page but confirmed live via `spot.all_symbols`'s full capture — see that endpoint's notes."""
  isMarginEnabled: bool
  """Whether this pair can be margin-traded."""
  enableTrading: bool
  """Whether trading is currently enabled on this pair."""
  feeCategory: int
  """Fee tier classification. Undocumented on this page but present live — see All Symbols."""
  makerFeeCoefficient: str
  """Maker fee multiplier."""
  takerFeeCoefficient: str
  """Taker fee multiplier."""
  st: bool
  """Special-treatment (risk warning) token indicator. Undocumented on this page but present live — see All Symbols."""
  callauctionIsEnabled: bool
  """Whether this pair currently uses a call-auction opening phase. Undocumented on this page but present live — see All Symbols."""
  callauctionPriceFloor: str | None
  """Call auction price floor, when in a call-auction phase."""
  callauctionPriceCeiling: str | None
  """Call auction price ceiling, when in a call-auction phase."""
  callauctionFirstStageStartTime: int | None
  """Call auction first stage start time, Unix ms, when applicable."""
  callauctionSecondStageStartTime: int | None
  """Call auction second stage start time, Unix ms, when applicable."""
  callauctionThirdStageStartTime: int | None
  """Call auction third stage start time, Unix ms, when applicable."""
  tradingStartTime: int | None
  """Scheduled trading start time, Unix ms, for a newly-listed pair not yet trading."""


_Type = SpotSymbolDetail
adapter = validator[_Type](_Type)  # type: ignore


class Symbol(RpcEndpoint):
  """`Get Symbol` — mixed into `Spot`, the product exposing `spot.symbol`."""

  async def symbol(
    self, symbol: str, *, validate: bool | None = None
  ) -> SpotSymbolDetail:
    """Get order-placement configuration for one trading pair: size/price increments and limits, margin eligibility, fee coefficients, and call-auction status.

    Args:
      symbol: Trading pair symbol, e.g. `BTC-USDT`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.request(
      'GET',
      f'/api/v2/symbols/{symbol}',
      validator=adapter,
      validate=validate,
    )
