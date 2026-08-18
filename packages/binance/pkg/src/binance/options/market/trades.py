from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class Trade(TypedDict):
  """One completed public trade."""

  id: NotRequired[int]
  """Trade ID."""
  tradeId: NotRequired[int]
  """Trade ID."""
  symbol: NotRequired[str]
  """Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000)."""
  price: NotRequired[str]
  """Completed trade price."""
  qty: NotRequired[str]
  """Completed trade quantity."""
  quoteQty: NotRequired[str]
  """Completed trade amount, in quote asset."""
  side: NotRequired[Literal[-1, 1]]
  """Completed trade direction."""
  time: NotRequired[Timestamp]
  """Trade time."""


class Trades(RpcEndpoint):
  """Get recent market trades."""

  async def trades(
    self,
    *,
    symbol: str,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[Trade]:
    """Get recent market trades.

    Args:
      symbol: Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000).
      limit: Number of result sets returned. Default 100, max 500.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/market-data#recent-trades-list)
    """
    params: dict = {
      'symbol': symbol,
    }
    if limit is not None:
      params['limit'] = limit
    _Response = list[Trade]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/eapi/v1/trades', params=params, validator=_validator, validate=validate
    )
