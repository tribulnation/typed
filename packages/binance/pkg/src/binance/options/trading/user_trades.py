from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class UserTrade(TypedDict):
  """One of the account's own trades."""

  id: NotRequired[int]
  """Unique ID."""
  tradeId: NotRequired[int]
  """Trade ID."""
  orderId: NotRequired[int]
  """Order ID."""
  symbol: NotRequired[str]
  """Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000)."""
  price: NotRequired[str]
  """Trade price."""
  quantity: NotRequired[str]
  """Trade quantity."""
  fee: NotRequired[str]
  """Fee. Negative values represent a fee deduction."""
  realizedProfit: NotRequired[str]
  """Realized profit/loss."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Order side."""
  type: NotRequired[Literal['LIMIT']]
  """Order type."""
  liquidity: NotRequired[Literal['TAKER', 'MAKER']]
  """Whether this fill was a taker or maker trade."""
  time: NotRequired[Timestamp]
  """Trade time."""
  priceScale: NotRequired[int]
  """Price precision."""
  quantityScale: NotRequired[int]
  """Quantity precision."""
  optionSide: NotRequired[Literal['CALL', 'PUT']]
  """Option side."""
  quoteAsset: NotRequired[str]
  """Quote asset."""


class UserTrades(RpcEndpoint):
  """Get trades for a specific account and symbol."""

  async def user_trades(
    self,
    *,
    symbol: str,
    from_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[UserTrade]:
    """Get trades for a specific account and symbol.

    Args:
      symbol: Option trading pair, formatted UNDERLYING-EXPIRYDATE-STRIKE-C|P, e.g. BTC-260925-145000-C (a BTC call expiring 2026-09-25 with strike 145000).
      from_id: Trade ID to fetch from. Defaults to the most recent trades.
      start_time: Start time.
      end_time: End time.
      limit: Number of result sets returned.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/trade#account-trade-list)
    """
    params: dict = {
      'symbol': symbol,
    }
    if from_id is not None:
      params['fromId'] = from_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[UserTrade]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/eapi/v1/userTrades',
      params=params,
      validator=_validator,
      validate=validate,
    )
