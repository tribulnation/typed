from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmMarginAccountTradeList(TypedDict):
  """PmMarginAccountTradeList."""

  commission: NotRequired[str]
  """Commission."""
  commissionAsset: NotRequired[str]
  """Commission Asset."""
  id: NotRequired[int]
  """ID."""
  isBestMatch: NotRequired[bool]
  """Is Best Match."""
  isBuyer: NotRequired[bool]
  """Is Buyer."""
  isMaker: NotRequired[bool]
  """Is Maker."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  price: NotRequired[str]
  """Price."""
  qty: NotRequired[str]
  """Qty."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  time: NotRequired[Timestamp]
  """Event time."""


class MarginTrades(RpcEndpoint):
  """Margin Account Trade List"""

  async def margin_trades(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    from_id: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[PmMarginAccountTradeList]:
    """Margin Account Trade List.

    Args:
      symbol: Symbol.
      order_id: Order id to act on.
      start_time: Timestamp in ms to get funding from INCLUSIVE.
      end_time: Timestamp in ms to get funding until INCLUSIVE.
      from_id: Trade ID to fetch from.
      limit: Number of results returned.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#margin-account-trade-list)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if from_id is not None:
      params['fromId'] = from_id
    if limit is not None:
      params['limit'] = limit
    _Response = list[PmMarginAccountTradeList]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/margin/myTrades',
      params=params,
      validator=_validator,
      validate=validate,
    )
