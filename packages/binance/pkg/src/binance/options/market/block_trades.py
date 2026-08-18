from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BlockTrade(TypedDict):
  """One completed public block trade."""

  id: NotRequired[int]
  """Trade ID."""
  tradeId: NotRequired[int]
  """Trade ID."""
  symbol: NotRequired[str]
  """Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000)."""
  price: NotRequired[str]
  """Trade price."""
  qty: NotRequired[str]
  """Trade quantity."""
  quoteQty: NotRequired[str]
  """Trade amount, in quote asset."""
  side: NotRequired[Literal[-1, 1]]
  """Trade direction."""
  time: NotRequired[Timestamp]
  """Trade time."""


class BlockTrades(RpcEndpoint):
  """Get recent block trades."""

  async def block_trades(
    self,
    *,
    symbol: str | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[BlockTrade]:
    """Get recent block trades.

    Args:
      symbol: Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000).
      limit: Number of records returned. Default 100, max 500.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/market-data#recent-block-trades-list)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if limit is not None:
      params['limit'] = limit
    _Response = list[BlockTrade]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/eapi/v1/blockTrades',
      params=params,
      validator=_validator,
      validate=validate,
    )
