from dataclasses import dataclass
from datetime import datetime
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class HistoricalMarketTrade(TypedDict):
  """One historical trade for a product."""

  trade_id: str
  """Unique identifier for the trade."""
  product_id: str
  """The trading pair the trade occurred on."""
  price: str
  """Trade price in quote currency."""
  size: str
  """Trade size in base currency."""
  time: datetime
  """Time the trade occurred."""
  side: Literal['BUY', 'SELL']
  """Which side of the book took liquidity."""
  exchange: NotRequired[str]
  """Venue the trade occurred on."""


class MarketTradesResponse(TypedDict):
  """A page of recent trades for a product."""

  trades: list[HistoricalMarketTrade]
  """Trades, newest first."""
  best_bid: NotRequired[str]
  """Current best bid price."""
  best_ask: NotRequired[str]
  """Current best ask price."""


@dataclass(frozen=True, kw_only=True)
class MarketTrades(RpcEndpoint):
  """`GET /api/v3/brokerage/market/products/{product_id}/ticker`."""

  async def market_trades(
    self,
    product_id: str,
    *,
    limit: int,
    start: int | None = None,
    end: int | None = None,
  ) -> MarketTradesResponse:
    """No authentication required. Get the most recent trades for one product from the public catalog. Named 'ticker' on the wire, but returns a trade-history page, not best bid/ask.

    Args:
      product_id: The trading pair, e.g. `BTC-USD`.
      limit: Number of trades to return.
      start: UNIX timestamp for the start of the requested window.
      end: UNIX timestamp for the end of the requested window.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/public/get-public-market-trades)
    """
    params: dict = {
      'limit': limit,
    }
    if start is not None:
      params['start'] = start
    if end is not None:
      params['end'] = end
    return await self.request(
      'GET',
      f'/api/v3/brokerage/market/products/{product_id}/ticker',
      params=params,
      validator=validator(MarketTradesResponse),
    )
