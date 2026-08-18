"""`spot.market_data.pre_trade` -- public Spot market data."""

from datetime import datetime
from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class PreTradeAskLevel(TypedDict):
  """One aggregated ask price level."""

  side: NotRequired[Literal['SELL']]
  """Indicates this level is an offer."""
  price: NotRequired[str]
  """Price level in the Central Limit Order Book (CLOB)."""
  qty: NotRequired[str]
  """The aggregated quantity at the price level."""
  count: NotRequired[int]
  """The number of orders in the price level."""
  submission_ts: NotRequired[datetime]
  """Timestamp the order at this price level was submitted."""
  publication_ts: NotRequired[datetime]
  """Timestamp the price level was last updated and published."""


class PreTradeBidLevel(TypedDict):
  """One aggregated bid price level."""

  side: NotRequired[Literal['BUY']]
  """Indicates this level is a bid."""
  price: NotRequired[str]
  """Price level in the Central Limit Order Book (CLOB)."""
  qty: NotRequired[str]
  """The aggregated quantity at the price level."""
  count: NotRequired[int]
  """The number of orders in the price level."""
  submission_ts: NotRequired[datetime]
  """Timestamp the order at this price level was submitted."""
  publication_ts: NotRequired[datetime]
  """Timestamp the price level was last updated and published."""


class PreTradeBook(TypedDict):
  """The top-10-level aggregated order book for a pair, plus reference/venue metadata."""

  symbol: NotRequired[str]
  """The symbol of the currency pair."""
  description: NotRequired[str]
  """The full description of the currency pair."""
  base_asset: NotRequired[str]
  """ISO 4217 currency code for the base asset."""
  base_dti_code: NotRequired[str]
  """Digital Token Identifier (DTI) code for the base asset."""
  base_dti_short_name: NotRequired[str]
  """DTI short name for the base asset."""
  quote_dti_code: NotRequired[str]
  """Digital Token Identifier (DTI) code for the quote asset."""
  quote_dti_short_name: NotRequired[str]
  """DTI short name for the quote asset."""
  base_notation: NotRequired[Literal['UNIT', 'NOML']]
  """Indicates how the base quantity is expressed: `UNIT` (nominal units) or `NOML` (notional value)."""
  quote_asset: NotRequired[str]
  """ISO 4217 currency in which the trading price is expressed."""
  quote_notation: NotRequired[Literal['MONE']]
  """Indicates that the price is expressed in monetary value."""
  venue: NotRequired[Literal['PGSL']]
  """ISO 10383 Market Identifier Code (MIC) of the trading platform where the order was submitted."""
  system: NotRequired[Literal['CLOB']]
  """Indicates the order system is a Central Limit Order Book."""
  bids: NotRequired[list[PreTradeBidLevel]]
  """Top-10 aggregated bid levels."""
  asks: NotRequired[list[PreTradeAskLevel]]
  """Top-10 aggregated ask levels."""


validate_pre_trade = validator(PreTradeBook)


class PreTrade(RpcEndpoint):
  """`spot.market_data.pre_trade`."""

  async def pre_trade(self, symbol: str) -> PreTradeBook:
    """Returns the price levels in the order book with aggregated order quantities at each price level. The top 10 levels are returned for each trading pair.

    Args:
      symbol: A list of symbols for the currency pairs.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/transparency/pre-trade-data)
    """
    params: dict = {
      'symbol': symbol,
    }

    return await self.request(
      '/0/public/PreTrade', params, validator=validate_pre_trade
    )
