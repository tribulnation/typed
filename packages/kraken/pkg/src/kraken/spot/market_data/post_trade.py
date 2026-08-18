"""`spot.market_data.post_trade` -- public Spot market data."""

from datetime import datetime
from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class PostTradeEntry(TypedDict):
  """One executed trade."""

  trade_id: NotRequired[str]
  """Kraken unique trade identifier."""
  price: NotRequired[str]
  """Trade price excluding fees and commissions."""
  quantity: NotRequired[str]
  """Unconsolidated trade quantity from execution."""
  symbol: NotRequired[str]
  """The symbol of the currency pair."""
  description: NotRequired[str]
  """The full description of the currency pair."""
  base_asset: NotRequired[str]
  """ISO 4217 currency code for the base asset."""
  base_notation: NotRequired[Literal['UNIT']]
  """Indicates that the quantity is expressed in nominal units."""
  quote_asset: NotRequired[str]
  """ISO 4217 currency in which the trading price is expressed."""
  quote_notation: NotRequired[Literal['MONE']]
  """Indicates that the price is expressed in monetary value."""
  trade_venue: NotRequired[str]
  """ISO 10383 Market Identifier Code (MIC) of the trading platform where the trade was executed."""
  trade_ts: NotRequired[datetime]
  """Timestamp the trade was matched in the engine, to microsecond precision."""
  publication_venue: NotRequired[str]
  """ISO 10383 Market Identifier Code (MIC) of the trading platform where the trade was published."""
  publication_ts: NotRequired[datetime]
  """Timestamp the trade was published to market data streams."""


class PostTradeResult(TypedDict):
  """A list of executed trades in ascending timestamp order."""

  last_ts: NotRequired[datetime]
  """Timestamp of the latest trade in the list. Can be used as the `from_ts` parameter when requesting the next batch of trades."""
  count: NotRequired[int]
  """The number of trades returned."""
  trades: NotRequired[list[PostTradeEntry]]
  """The trades, in ascending timestamp order."""


validate_post_trade = validator(PostTradeResult)


class PostTrade(RpcEndpoint):
  """`spot.market_data.post_trade`."""

  async def post_trade(
    self,
    *,
    symbol: str | None = None,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    count: int | None = None,
  ) -> PostTradeResult:
    """Returns a list of trades on the spot exchange. If no filter parameters are specified, the last 1000 trades for all pairs are received.

    Args:
      symbol: Filter the results to the currency pair.
      from_ts: Filter the results to include the trades after this timestamp.
      to_ts: Filter the results to include the trades before or at this timestamp.
      count: The maximum number of trades to return.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/transparency/post-trade-data)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if from_ts is not None:
      params['from_ts'] = from_ts
    if to_ts is not None:
      params['to_ts'] = to_ts
    if count is not None:
      params['count'] = count

    return await self.request(
      '/0/public/PostTrade', params, validator=validate_post_trade
    )
