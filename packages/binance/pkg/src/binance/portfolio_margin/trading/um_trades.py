from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmUmAccountTradeList(TypedDict):
  """PmUmAccountTradeList."""

  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  id: NotRequired[int]
  """ID."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Side."""
  price: NotRequired[str]
  """Price."""
  qty: NotRequired[str]
  """Qty."""
  realizedPnl: NotRequired[str]
  """Realized Pnl."""
  quoteQty: NotRequired[str]
  """Quote Qty."""
  commission: NotRequired[str]
  """Commission."""
  commissionAsset: NotRequired[str]
  """Commission Asset."""
  time: NotRequired[Timestamp]
  """Event time."""
  buyer: NotRequired[bool]
  """Buyer."""
  maker: NotRequired[bool]
  """Maker."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """BOTH means that it is the position of One-way Mode."""


class UmTrades(RpcEndpoint):
  """UM Account Trade List"""

  async def um_trades(
    self,
    *,
    symbol: str,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    from_id: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[PmUmAccountTradeList]:
    """Get trades for a specific account and UM symbol.

    Args:
      symbol: Symbol.
      start_time: Timestamp in ms to get funding from INCLUSIVE.
      end_time: Timestamp in ms to get funding until INCLUSIVE.
      from_id: Trade ID to fetch from.
      limit: Number of results returned.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#um-account-trade-list)
    """
    params: dict = {
      'symbol': symbol,
    }
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if from_id is not None:
      params['fromId'] = from_id
    if limit is not None:
      params['limit'] = limit
    _Response = list[PmUmAccountTradeList]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/um/userTrades',
      params=params,
      validator=_validator,
      validate=validate,
    )
