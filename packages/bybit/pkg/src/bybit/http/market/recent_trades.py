"""`GET /v5/market/recent-trade` — Get Recent Public Trades."""

from typing_extensions import Literal, NotRequired, TypedDict
from bybit.core import Endpoint, validator


class PublicTrade(TypedDict):
  """One public trade printed on the tape."""

  execId: str
  """Execution identifier of the trade."""
  symbol: str
  """Symbol name."""
  price: str
  """Trade price."""
  size: str
  """Trade size."""
  side: Literal['Buy', 'Sell']
  """Side of the taker."""
  time: str
  """Trade time, as a millisecond timestamp."""
  isBlockTrade: bool
  """Whether the trade was a block trade."""
  isRPITrade: NotRequired[bool]
  """Whether the trade was a retail price improvement trade; absent for options."""
  seq: NotRequired[str]
  """Cross sequence number of the trade."""
  mP: NotRequired[str]
  """Mark price at execution; options only."""
  iP: NotRequired[str]
  """Index price at execution; options only."""
  mIv: NotRequired[str]
  """Mark implied volatility at execution; options only."""
  iv: NotRequired[str]
  """Implied volatility at execution; options only."""


class RecentTrades(TypedDict):
  """Recent public trades."""

  category: Literal['spot', 'linear', 'inverse', 'option']
  """Product type."""
  list: list[PublicTrade]
  """Trades, sorted by trade time in descending order."""


adapter = validator[RecentTrades](RecentTrades)


class RecentTradesEndpoint(Endpoint):
  """`Get Recent Public Trades` — mixed into the router that owns `market.recent_trades`."""

  async def recent_trades(
    self,
    *,
    category: Literal['spot', 'linear', 'inverse', 'option'],
    symbol: str | None = None,
    base_coin: str | None = None,
    option_type: Literal['Call', 'Put'] | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> RecentTrades:
    """Get the most recent public trades for a symbol, newest first.

    Args:
      category: Product type.
      symbol: Symbol name in uppercase, for example `BTCUSDT`. Required for spot, linear and inverse.
      base_coin: Base coin in uppercase. Applies to option only; defaults to `BTC`.
      option_type: Option type filter. Applies to option only.
      limit: Number of trades per page. Range [1, 60] with a default of 60 for spot, and [1, 1000] with a default of 500 otherwise.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/recent-trade)
    """
    params: dict = {
      'category': category,
    }
    if symbol is not None:
      params['symbol'] = symbol
    if base_coin is not None:
      params['baseCoin'] = base_coin
    if option_type is not None:
      params['optionType'] = option_type
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', '/v5/market/recent-trade', params=params)
    return self.result(r, adapter, validate)
